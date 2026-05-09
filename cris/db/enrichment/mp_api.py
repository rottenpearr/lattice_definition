"""
Materials Project API клиент.
Ключ задаётся через переменную окружения MP_API_KEY.
Получить ключ (бесплатно): https://materialsproject.org/api
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
    sg_number: int
    sg_symbol: str
    energy_above_hull: float
    band_gap: Optional[float]
    entry_url: str


def search(formula: str, max_results: int = 5) -> list[MpEntry]:
    api_key = os.getenv("MP_API_KEY", "")
    if not api_key:
        print("[MP] MP_API_KEY не задан")
        return []
    try:
        resp = requests.get(
            f"{MP_BASE}/materials/summary/",
            headers={"X-API-KEY": api_key},
            params={
                "formula": formula,
                "fields": "material_id,formula_pretty,symmetry,energy_above_hull,band_gap",
                "_limit": max_results,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
    except Exception as e:
        print(f"[MP] {e}")
        return []
    entries = []
    for item in data:
        sym = item.get("symmetry", {})
        mp_id = item.get("material_id", "")
        entries.append(MpEntry(
            mp_id=mp_id,
            formula=item.get("formula_pretty", ""),
            sg_number=sym.get("number", 0),
            sg_symbol=sym.get("symbol", ""),
            energy_above_hull=item.get("energy_above_hull", 0.0) or 0.0,
            band_gap=item.get("band_gap"),
            entry_url=f"https://materialsproject.org/materials/{mp_id}",
        ))
    return sorted(entries, key=lambda e: e.energy_above_hull)
