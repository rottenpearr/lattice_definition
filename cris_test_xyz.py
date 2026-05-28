"""
Тест библиотеки cris-core с реальным XYZ-файлом.

Установка:
    pip install -e "C:\\Users\\arbuz\\PycharmProjects\\lattice_definition"

Запуск:
    python cris_test_xyz.py
    python cris_test_xyz.py path/to/your/file.xyz
"""

import sys
from pathlib import Path

from cris import identify, load_xyz

# -- Выбираем файл --------------------------------------------------------------
if len(sys.argv) > 1:
    xyz_path = Path(sys.argv[1])
else:
    # Берём NaCl из датасета — 57 атомов, типичная FCC-структура
    xyz_path = Path(__file__).parent / "data" / "db" / "xyz" / "1000041.xyz"

if not xyz_path.exists():
    print(f"Файл не найден: {xyz_path}")
    sys.exit(1)

# -- Читаем XYZ ----------------------------------------------------------------
sites = load_xyz(xyz_path)
print(f"Файл    : {xyz_path.name}")
print(f"Атомов  : {len(sites)}")
print(f"Пример  : {sites[0]}")
print()

# -- Распознавание (ML-методы, без БД) ----------------------------------------
print("Запускаю распознавание...")
result = identify(sites)

print(f"\n{'-'*40}")
print(f"  Тип решётки : {result.lattice_type} ({result.lattice_confidence:.0%})")
print(f"  Вещество    : {result.substance} ({result.substance_confidence:.0%})")
print(f"{'-'*40}")

# -- Топ-3 по каждому методу ---------------------------------------------------
print("\nДетали по методам:")
for entry in result.ml_results:
    print(f"\n  [{entry['method']}]")
    for pred in entry["predictions"][:3]:
        cls  = pred.get("class") or pred.get("lattice_name", "?")
        conf = pred.get("confidence", 0)
        bar  = "#" * int(conf * 20)
        print(f"    {cls:<28} {conf:.1%}  {bar}")
