"""
Клиент для Materials Project API.
Документация: https://api.materialsproject.org/

Требует API-ключ: https://materialsproject.org/api (бесплатная регистрация).
Ключ задаётся через переменную окружения MP_API_KEY.
"""
import os
import requests
from dataclasses import dataclass
from typing import Optional

MP_BASE = "https://api.materialsproject.org"


@dataclass
class MpEntry:
    mp_id: str
    formula: str
    space_group_number: int
    space_group_symbol: str
    energy_above_hull: float   # термодинамическая стабильность (eV/atom)
    band_gap: Optional[float]
    formation_energy: Optional[float]
    entry_url: str


def _headers() -> dict:
    api_key = os.getenv("MP_API_KEY", "")
    return {"X-API-KEY": api_key} if api_key else {}


def search_by_formula(formula: str, max_results: int = 5) -> list[MpEntry]:
    """
    Ищет структуры в Materials Project по формуле.
    Возвращает список записей, отсортированных по стабильности.
    """
    if not os.getenv("MP_API_KEY"):
        print("[MP] MP_API_KEY не задан, запрос пропущен")
        return []

    try:
        resp = requests.get(
            f"{MP_BASE}/materials/summary/",
            headers=_headers(),
            params={
                "formula": formula,
                "fields": "material_id,formula_pretty,symmetry,energy_above_hull,"
                          "band_gap,formation_energy_per_atom",
                "_limit": max_results,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
    except Exception as e:
        print(f"[MP] Ошибка запроса: {e}")
        return []

    entries = []
    for item in data:
        sym = item.get("symmetry", {})
        mp_id = item.get("material_id", "")
        entries.append(MpEntry(
            mp_id=mp_id,
            formula=item.get("formula_pretty", ""),
            space_group_number=sym.get("number", 0),
            space_group_symbol=sym.get("symbol", ""),
            energy_above_hull=item.get("energy_above_hull", 0.0) or 0.0,
            band_gap=item.get("band_gap"),
            formation_energy=item.get("formation_energy_per_atom"),
            entry_url=f"https://materialsproject.org/materials/{mp_id}",
        ))
    return sorted(entries, key=lambda e: e.energy_above_hull)
