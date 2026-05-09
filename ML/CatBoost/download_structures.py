"""
Скачивает структуры урановых соединений из Materials Project API
и сохраняет в data/structures/micro/source/ в формате XYZ.

API-ключ читается из .env файла (MP_API_KEY=...) или передаётся через --api-key.

Использование:
    python ML/CatBoost/download_structures.py
    python ML/CatBoost/download_structures.py --limit 50
    python ML/CatBoost/download_structures.py --formula UC --limit 20

Зависимости:
    pip install mp-api python-dotenv
"""

import argparse
import os
from pathlib import Path

from mp_api.client import MPRester
from pymatgen.io.xyz import XYZ

# Путь для сохранения структур
OUT_DIR = Path(__file__).parent.parent.parent / "data" / "structures" / "micro" / "source"

# Элементы для поиска
SEARCH_ELEMENTS = ["U"]


def load_api_key(cli_key: str = None) -> str:
    """Читает API-ключ из аргумента CLI, затем из .env, затем из переменной окружения."""
    if cli_key:
        return cli_key

    # Попытка прочитать .env вручную
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("MP_API_KEY=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")

    # Переменная окружения
    key = os.environ.get("MP_API_KEY")
    if key:
        return key

    raise ValueError(
        "API-ключ не найден. Добавьте MP_API_KEY=<ключ> в файл .env "
        "или передайте через --api-key."
    )


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

        search_kwargs = dict(
            fields=["material_id", "formula_pretty", "structure", "symmetry"],
            deprecated=False,
        )

        if formula:
            search_kwargs["formula"] = formula
        else:
            search_kwargs["elements"] = SEARCH_ELEMENTS

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

        safe_formula = formula_pretty.replace(" ", "")
        filename = f"{safe_formula}_{mp_id}.xyz"
        filepath = OUT_DIR / filename

        if filepath.exists():
            print(f"  Уже есть: {filename}")
            skipped += 1
            continue

        try:
            spacegroup = doc.symmetry.symbol if doc.symmetry else "unknown"
            comment = f"{formula_pretty} {mp_id} sg={spacegroup}"
            structure_to_xyz(structure, filepath, comment)
            print(f"  Сохранён: {filename}  ({len(structure.sites)} атомов, {spacegroup})")
            saved += 1
        except Exception as e:
            print(f"  Ошибка {mp_id}: {e}")

    print(f"\nГотово: сохранено {saved}, пропущено {skipped}.")
    print(f"Папка: {OUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Скачать структуры из Materials Project")
    parser.add_argument("--api-key", default=None, help="MP API ключ (или MP_API_KEY в .env)")
    parser.add_argument("--limit", type=int, default=50, help="Максимум структур (по умолчанию 50)")
    parser.add_argument("--formula", type=str, default=None, help="Фильтр по формуле, например 'UC' или 'UN2'")
    args = parser.parse_args()

    key = load_api_key(args.api_key)
    download_structures(api_key=key, limit=args.limit, formula=args.formula)
