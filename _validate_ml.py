# -*- coding: utf-8 -*-
"""
Валидация ML-моделей на структурах из БД.
Запуск: python _validate_ml.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from cris.db.connection import get_cursor
from cris.core.coordinates import shift_coordinates, normalize_coordinates
from cris.core.ml_predict import predict_catboost, predict_rf, resolve_lattice_ids

ROOT = Path(".")

with get_cursor() as cur:
    cur.execute("""
        SELECT rs.name, rs.formula, rs.xyz_path, lt.name_en
        FROM reference_structure rs
        JOIN lattice_type lt ON lt.id = rs.lattice_type_id
        WHERE rs.xyz_path IS NOT NULL AND rs.xyz_path != ''
        ORDER BY rs.id
    """)
    rows = cur.fetchall()

def load_xyz(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    n = int(lines[0])
    coords = []
    for line in lines[2:2+n]:
        parts = line.split()
        if len(parts) >= 4:
            coords.append([parts[0], float(parts[1]), float(parts[2]), float(parts[3])])
    return coords

cb_correct = rf_correct = total = 0

header = f"{'Структура':<18} {'Истина':<16} {'CatBoost':<16} {'Conf':>5}  {'RF':<16} {'Conf':>5}"
print(header)
print("-" * 80)

for name, formula, xyz_path, true_label in rows:
    xyz = ROOT / xyz_path
    if not xyz.exists():
        continue

    try:
        raw = load_xyz(xyz)
        norm = normalize_coordinates(shift_coordinates(raw))

        cb_preds = resolve_lattice_ids(predict_catboost(norm))
        rf_preds = predict_rf(norm)

        cb_label = cb_preds[0]["lattice_name"] if cb_preds else "—"
        cb_conf  = cb_preds[0]["confidence"]   if cb_preds else 0.0
        rf_label = rf_preds[0]["class"]        if rf_preds else "—"
        rf_conf  = rf_preds[0]["confidence"]   if rf_preds else 0.0

        cb_ok = (cb_label == true_label)
        if cb_ok: cb_correct += 1
        total += 1

        cb_mark = "OK" if cb_ok else "  "
        print(f"{name:<18} {true_label:<16} {cb_label:<14} {cb_conf:>5.2f}  {cb_mark}  {rf_label:<16} {rf_conf:>5.2f}")

    except Exception as e:
        print(f"{name:<18} ERROR: {e}")

print("-" * 80)
if total:
    print(f"CatBoost accuracy: {cb_correct}/{total} = {cb_correct/total*100:.1f}%")
    print(f"(RF предсказывает соединение, а не тип решётки — точность не считаем)")
