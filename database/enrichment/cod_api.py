"""
Клиент для Crystallography Open Database (COD).
REST API: https://www.crystallography.net/cod/result.php

Пример: найти структуры по формуле и номеру пространственной группы,
        получить COD ID, DOI статьи, ссылку для скачивания CIF.
"""
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
    space_group_number: int
    space_group_hm: str
    cell_a: float
    cell_b: float
    cell_c: float
    doi: str
    cif_url: str
    entry_url: str


def search_by_formula(formula: str, space_group_number: Optional[int] = None,
                      max_results: int = 5) -> list[CodEntry]:
    """
    Ищет структуры в COD по химической формуле.
    formula: строка вида 'NaCl', 'UC', 'U2N3'
    Возвращает список найденных записей (может быть пустым).
    """
    params = {
        "format": "json",
        "formula": formula,
    }
    if space_group_number:
        params["sg_number"] = space_group_number

    try:
        resp = requests.get(COD_RESULT_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[COD] Ошибка запроса: {e}")
        return []

    entries = []
    for item in data[:max_results]:
        try:
            cod_id = int(item.get("file", 0))
            entries.append(CodEntry(
                cod_id=cod_id,
                formula=item.get("formula", ""),
                space_group_number=int(item.get("sg_number", 0) or 0),
                space_group_hm=item.get("sg", ""),
                cell_a=float(item.get("a", 0) or 0),
                cell_b=float(item.get("b", 0) or 0),
                cell_c=float(item.get("c", 0) or 0),
                doi=item.get("doi", ""),
                cif_url=COD_CIF_URL.format(cod_id=cod_id),
                entry_url=COD_ENTRY_URL.format(cod_id=cod_id),
            ))
        except (ValueError, TypeError):
            continue
    return entries


def get_cif_text(cod_id: int) -> Optional[str]:
    """Скачать CIF-текст для записи COD (для последующего сохранения в файл)."""
    try:
        resp = requests.get(COD_CIF_URL.format(cod_id=cod_id), timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[COD] Не удалось скачать CIF {cod_id}: {e}")
        return None
