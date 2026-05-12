"""
Загружает KDE-датасет из data/kde_arrays/ для обучения CatBoost.

Каждая итерация структуры — несколько CSV-файлов (по одному на ион).
Ионы усредняются → один вектор на итерацию.

Метка (тип решётки) берётся из data/kde_arrays/labels.csv (если есть),
иначе извлекается из имени папки структуры (fallback).

Сгенерировать labels.csv:
    python cris/tools/dataset_generation/generate_labels.py
"""

import csv
import sys
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

KDE_DIR    = ROOT / "data" / "kde_arrays"
LABELS_CSV = KDE_DIR / "labels.csv"

# ─── Fallback: извлечение метки из имени папки ────────────────────────────────

from cris.tools.dataset_generation.naming import lattice_type_from_stem, get_source_stem

_PRESET_TO_LATTICE = {
    "NaCl": "cubic_f", "UN": "cubic_f", "UC": "cubic_f", "UO2": "cubic_f",
    "Al":   "cubic_f", "Cu": "cubic_f", "CsCl": "cubic_p", "Fe": "cubic_i",
}

def _fallback_label(name: str) -> str | None:
    """Определяет метку из имени без labels.csv."""
    source = get_source_stem(name)
    lt = lattice_type_from_stem(source)
    if lt:
        return lt
    first = source.split("_")[0]
    return _PRESET_TO_LATTICE.get(first)


# ─── Загрузка labels.csv ──────────────────────────────────────────────────────

def load_labels(labels_csv: Path = LABELS_CSV) -> dict[str, str]:
    """Загружает labels.csv → {name: lattice_type}. Пустой словарь если файл не найден."""
    if not labels_csv.exists():
        return {}
    with open(labels_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["name"]: row["lattice_type"] for row in reader}


# ─── Загрузка одной итерации ─────────────────────────────────────────────────

def load_iteration(iter_dir: Path) -> np.ndarray | None:
    """Усредняет KDE-массивы всех ионов в одной итерации → один вектор."""
    csvs = list(iter_dir.glob("*.csv"))
    if not csvs:
        return None
    arrays = []
    for csv_path in csvs:
        try:
            arr = pd.read_csv(csv_path)["kde_values"].values.astype(float)
            arrays.append(arr)
        except Exception:
            continue
    if not arrays:
        return None
    return np.mean(arrays, axis=0)


# ─── Загрузка датасета ────────────────────────────────────────────────────────

def load_dataset(kde_dir: Path = KDE_DIR, verbose: bool = True):
    """
    Загружает весь датасет из kde_dir (рекурсивно: micro/ и macro/).

    Возвращает:
        X     — np.ndarray (n_samples, kde_size)
        y     — np.ndarray (n_samples,) — строковые метки типов решёток
        names — list[str] — имя структуры для каждого сэмпла
    """
    labels_map = load_labels()
    if verbose:
        if labels_map:
            print(f"  labels.csv загружен: {len(labels_map)} записей")
        else:
            print("  labels.csv не найден — используется fallback по именам файлов")
            print("  Рекомендуется: python cris/tools/dataset_generation/generate_labels.py\n")

    X, y, names = [], [], []
    skipped = []

    # Сканируем micro/ и macro/
    for subdir in ["micro", "macro"]:
        sub_path = kde_dir / subdir
        if not sub_path.exists():
            continue

        for struct_dir in sorted(sub_path.iterdir()):
            if not struct_dir.is_dir():
                continue

            name = struct_dir.name

            # Приоритет: labels.csv, затем fallback
            label = labels_map.get(name) or _fallback_label(name)
            if label is None:
                skipped.append(name)
                continue

            iter_dirs = sorted(
                [d for d in struct_dir.iterdir() if d.is_dir() and d.name.isdigit()],
                key=lambda d: int(d.name),
            )
            n_loaded = 0
            for iter_dir in iter_dirs:
                vec = load_iteration(iter_dir)
                if vec is not None:
                    X.append(vec)
                    y.append(label)
                    names.append(name)
                    n_loaded += 1

            if verbose:
                print(f"  {name:45s}  [{label}]  {n_loaded} сэмплов")

    if skipped and verbose:
        print(f"\n  Пропущено (метка не определена): {', '.join(skipped)}")
        print("  → Запустите generate_labels.py для добавления меток")

    if not X:
        return np.array([]), np.array([]), []

    return np.array(X), np.array(y), names
