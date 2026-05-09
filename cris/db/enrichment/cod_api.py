"""Клиент Crystallography Open Database (COD) REST API."""
import requests
from dataclasses import dataclass
from typing import Optional

COD_RESULT_URL = "https://www.crystallography.net/cod/result.php"
COD_CIF_URL    = "https://www.crystallography.net/cod/{cod_id}.cif"
COD_ENTRY_URL  = "https://www.crystallography.net/cod/{cod_id}.html"


@dataclass
class CodEntry:
    cod_id: int
    formula: str
    sg_number: int
    sg_hm: str
    cell_a: float
    doi: str
    cif_url: str
    entry_url: str


def search(formula: str, sg_number: Optional[int] = None,
           max_results: int = 5) -> list[CodEntry]:
    params: dict = {"format": "json", "formula": formula}
    if sg_number:
        params["sg_number"] = sg_number
    try:
        resp = requests.get(COD_RESULT_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[COD] {e}")
        return []
    entries = []
    for item in data[:max_results]:
        try:
            cod_id = int(item.get("file", 0))
            entries.append(CodEntry(
                cod_id=cod_id,
                formula=item.get("formula", ""),
                sg_number=int(item.get("sg_number", 0) or 0),
                sg_hm=item.get("sg", ""),
                cell_a=float(item.get("a", 0) or 0),
                doi=item.get("doi", ""),
                cif_url=COD_CIF_URL.format(cod_id=cod_id),
                entry_url=COD_ENTRY_URL.format(cod_id=cod_id),
            ))
        except (ValueError, TypeError):
            continue
    return entries


def download_cif(cod_id: int) -> Optional[str]:
    try:
        resp = requests.get(COD_CIF_URL.format(cod_id=cod_id), timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[COD] CIF {cod_id}: {e}")
        return None
