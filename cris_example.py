"""
Пример использования cris-core как Python-библиотеки.

Установка (локально, в режиме editable):
    pip install -e .

Запуск:
    python cris_example.py
"""

from cris import identify, __version__

print(f"cris-core v{__version__}\n")

# ── Пример 1: UN unit cell (NaCl-тип, ГЦК, a=4.89 Å) ────────────────────────
# Дефолтный образец из Workspace-а
un_cell = [
    {"label": "U", "x": 0.0, "y": 0.0, "z": 0.0},
    {"label": "U", "x": 0.5, "y": 0.5, "z": 0.0},
    {"label": "U", "x": 0.5, "y": 0.0, "z": 0.5},
    {"label": "U", "x": 0.0, "y": 0.5, "z": 0.5},
    {"label": "N", "x": 0.5, "y": 0.5, "z": 0.5},
    {"label": "N", "x": 0.0, "y": 0.0, "z": 0.5},
    {"label": "N", "x": 0.0, "y": 0.5, "z": 0.0},
    {"label": "N", "x": 0.5, "y": 0.0, "z": 0.0},
]

print("=== Пример 1: UN (ML-методы, без БД) ===")
result = identify(un_cell)          # по умолчанию: catboost + catboost_substance + rf
print(result)                       # CrisResult(lattice='cubic' (87%), substance='UN' (91%))
print(f"  Тип решётки : {result.lattice_type} ({result.lattice_confidence:.0%})")
print(f"  Вещество    : {result.substance} ({result.substance_confidence:.0%})")

# ── Пример 2: только один метод ──────────────────────────────────────────────
print("\n=== Пример 2: только CatBoost-сингония ===")
result2 = identify(un_cell, methods=["catboost"])
print(f"  Тип решётки : {result2.lattice_type} ({result2.lattice_confidence:.0%})")

# ── Пример 3: список вместо dict ─────────────────────────────────────────────
print("\n=== Пример 3: ввод через список ===")
result3 = identify([
    ["U", 0.0, 0.0, 0.0],
    ["U", 0.5, 0.5, 0.0],
    ["U", 0.5, 0.0, 0.5],
    ["U", 0.0, 0.5, 0.5],
    ["N", 0.5, 0.5, 0.5],
    ["N", 0.0, 0.0, 0.5],
    ["N", 0.0, 0.5, 0.0],
    ["N", 0.5, 0.0, 0.0],
])
print(f"  {result3}")

# ── Пример 4: с поиском по БД (требует PostgreSQL + .env) ────────────────────
print("\n=== Пример 4: с поиском по БД ===")
try:
    result4 = identify(un_cell, methods=["catboost", "catboost_substance", "rf", "db"])
    print(f"  {result4}")
    if result4.db_match_name:
        print(f"  DB-совпадение: {result4.db_match_name} (формула: {result4.db_match_formula})")
    else:
        print("  DB-совпадений не найдено")
except Exception as e:
    print(f"  DB недоступна: {e}")

# ── Полные предсказания по каждому методу ────────────────────────────────────
print("\n=== Детали ML (топ-3 по каждому методу) ===")
for entry in result.ml_results:
    print(f"\n  [{entry['method']}]")
    for pred in entry["predictions"][:3]:
        cls  = pred.get("class") or pred.get("lattice_name", "?")
        conf = pred.get("confidence", 0)
        print(f"    {cls:<30} {conf:.1%}")
