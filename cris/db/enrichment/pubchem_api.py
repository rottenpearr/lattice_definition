"""
PubChem REST API — получение физико-химических свойств вещества.

Документация: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
Ключ API не нужен, rate limit: 5 req/s.
"""
import requests
from typing import Optional
from cris.logger import logger

_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
_TIMEOUT = 10


def _get(url: str) -> Optional[dict]:
    try:
        r = requests.get(url, timeout=_TIMEOUT)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        logger.warning("PubChem request failed: {} | url={}", e, url)
        return None


def get_properties(formula: str) -> dict:
    """
    Ищет вещество по формуле, возвращает словарь физических свойств.

    Возвращаемые поля (если найдены):
        molecular_weight, melting_point, boiling_point, density,
        color, iupac_name, hazard_class, pubchem_cid
    """
    # 1. Ищем CID по формуле
    url = f"{_BASE}/compound/formula/{formula}/cids/JSON"
    data = _get(url)
    if not data:
        logger.debug("PubChem: no CID for formula '{}'", formula)
        return {}

    cids = data.get("IdentifierList", {}).get("CID", [])
    if not cids:
        return {}
    cid = cids[0]

    # 2. Получаем свойства по CID
    props = "MolecularWeight,IUPACName,MolecularFormula"
    url_props = f"{_BASE}/compound/cid/{cid}/property/{props}/JSON"
    prop_data = _get(url_props)

    result: dict = {"pubchem_cid": cid}

    if prop_data:
        p = prop_data.get("PropertyTable", {}).get("Properties", [{}])[0]
        if p.get("MolecularWeight"):
            result["molecular_weight"] = f"{p['MolecularWeight']} г/моль"
        if p.get("IUPACName"):
            result["iupac_name"] = p["IUPACName"]

    # 3. Получаем экспериментальные данные (температуры, плотность и пр.)
    url_exp = f"{_BASE}/compound/cid/{cid}/JSON"
    full_data = _get(url_exp)
    if full_data:
        _extract_experimental(full_data, result)

    logger.debug("PubChem: got {} properties for '{}' (CID={})", len(result), formula, cid)
    return result


def _extract_experimental(data: dict, result: dict) -> None:
    """Извлекает экспериментальные свойства из полного ответа PubChem."""
    try:
        sections = (
            data.get("PC_Compounds", [{}])[0]
            .get("props", [])
        )
        for prop in sections:
            urn = prop.get("urn", {})
            label = urn.get("label", "")
            name  = urn.get("name", "")
            value = prop.get("value", {})
            val_str = (
                value.get("sval")
                or value.get("fval")
                or value.get("ival")
            )
            if not val_str:
                continue
            val_str = str(val_str)

            if label == "Melting Point" and "melting_point" not in result:
                result["melting_point"] = val_str
            elif label == "Boiling Point" and "boiling_point" not in result:
                result["boiling_point"] = val_str
            elif label == "Density" and "density" not in result:
                result["density"] = val_str
            elif label == "Color/Form" and "color" not in result:
                result["color"] = val_str
            elif label == "GHS Hazard Statements" and "hazard_ghs" not in result:
                result["hazard_ghs"] = val_str[:200]
    except Exception as e:
        logger.debug("PubChem: experimental extraction error: {}", e)
