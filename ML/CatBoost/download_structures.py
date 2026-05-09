"""
Скачивает структуры урановых соединений из Materials Project API
и сохраняет в data/structures/accurate/ в формате XYZ.

Использование:
    python ML/CatBoost/download_structures.py --api-key YOUR_KEY
    python ML/CatBoost/download_structures.py --api-key YOUR_KEY --limit 50
    python ML/CatBoost/download_structures.py --api-key YOUR_KEY --formula UC

Зависимости:
    pip install mp-api
"""

import argparse
import os
from pathlib import Path

from mp_api.client import MPRester
from pymatgen.io.xyz import XYZ

# Путь для сохранения структур
OUT_DIR = Path(__file__).parent.parent.parent / "data" / "structures" / "accurate"

# Элементы для поиска — только соединения урана
SEARCH_ELEMENTS = ["U"]

# Дополнительный фильтр по формуле (None = все урановые соединения)
FORMULA_FILTER = None


def structure_to_xyz(structure, filepath: Path, comment: str = ""):
    """Конвертирует pymatgen Structure в XYZ-файл."""
    sites = structure.sites
    lines = [
        str(len(sites)),
        comment or structure.formula,
    ]
    for site in sites:
        coords = site.coords  # Декартовы координаты в Å
        lines.append(f" {site.specie.symbol}    {coords[0]:.6f}    {coords[1]:.6f}    {coords[2]:.6f}")
    filepath.write_text("\n".join(lines) + "\n")


def download_structures(api_key: str, limit: int = 50, formula: str = None):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Подключение к Materials Project API...")
    with MPRester(api_key=api_key) as mpr:

        # Параметры поиска
        search_kwargs = dict(
            elements=SEARCH_ELEMENTS,
            fields=["material_id", "formula_pretty", "structure", "symmetry", "energy_above_hull"],
            num_chunks=1,
        )

        # Фильтр по формуле если указан
        if formula:
            search_kwargs["formula"] = formula
            del search_kwargs["elements"]

        # Фильтр по стабильности: только стабильные или близкие к стабильным структуры
        search_kwargs["energy_above_hull"] = (0, 0.1)  # eV/atom

        print(f"Поиск структур (лимит: {limit})...")
        docs = mpr.materials.search(**search_kwargs)

    saved = 0
    skipped = 0

    for doc in docs:
        if saved >= limit:
            break

        mp_id = doc.material_id
        formula_pretty = doc.formula_pretty
        structure = doc.structure

        # Имя файла: formula_mpid.xyz, например UC_mp-2489.xyz
        safe_formula = formula_pretty.replace(" ", "")
        filename = f"{safe_formula}_{mp_id}.xyz"
        filepath = OUT_DIR / filename

        # Пропускаем если уже скачан
        if filepath.exists():
            print(f"  Уже есть: {filename}")
            skipped += 1
            continue

        try:
            spacegroup = doc.symmetry.symbol if doc.symmetry else "unknown"
            e_hull = doc.energy_above_hull
            comment = f"{formula_pretty} {mp_id} sg={spacegroup} e_hull={e_hull:.4f}"
            structure_to_xyz(structure, filepath, comment)
            print(f"  Сохранён: {filename}  ({len(structure.sites)} атомов, {spacegroup})")
            saved += 1
        except Exception as e:
            print(f"  Ошибка {mp_id}: {e}")

    print(f"\nГотово: сохранено {saved}, пропущено {skipped}.")
    print(f"Папка: {OUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Скачать структуры из Materials Project")
    parser.add_argument("--api-key", required=True, help="MP API ключ")
    parser.add_argument("--limit", type=int, default=50, help="Максимум структур (по умолчанию 50)")
    parser.add_argument("--formula", type=str, default=None, help="Фильтр по формуле, например 'UC' или 'UN2'")
    args = parser.parse_args()

    download_structures(api_key=args.api_key, limit=args.limit, formula=args.formula)
