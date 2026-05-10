"""
Загружает KDE-датасет из data/kde_arrays/macro/ для обучения CatBoost.

Каждая итерация структуры — несколько CSV-файлов (по одному на ион).
Ионы усредняются → один вектор на итерацию.
Метка (тип решётки) извлекается из имени папки структуры.
"""

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
KDE_DIR = ROOT / "data" / "kde_arrays" / "macro"

# Все 14 типов решёток — для определения метки из имени папки
LATTICE_TYPES = [
    "cubic_p", "cubic_i", "cubic_f",
    "tetra_p", "tetra_i",
    "ortho_p", "ortho_i", "ortho_f", "ortho_c",
    "hex_p", "trig_r",
    "mono_p", "mono_c",
    "triclinic",
]

# Пресеты → тип решётки
PRESET_TO_LATTICE = {
    "NaCl": "cubic_f",
    "UN":   "cubic_f",
    "UC":   "cubic_f",
    "UO2":  "cubic_f",
    "Al":   "cubic_f",
    "Cu":   "cubic_f",
    "CsCl": "cubic_p",
    "Fe":   "cubic_i",
}


def extract_label(folder_name: str) -> str | None:
    """Определяет тип решётки по имени папки структуры.

    Примеры:
        hex_p_Zn_4x4x4   → hex_p
        cubic_f_Al_5x5x5 → cubic_f
        NaCl_5x5x5       → cubic_f (через PRESET_TO_LATTICE)
        UN_4x4x4         → cubic_f
    """
    for lt in LATTICE_TYPES:
        if folder_name.startswith(lt + "_") or folder_name == lt:
            return lt
    first = folder_name.split("_")[0]
    return PRESET_TO_LATTICE.get(first)


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


def load_dataset(kde_dir: Path = KDE_DIR, verbose: bool = True):
    """
    Загружает весь датасет из kde_dir.

    Возвращает:
        X     — np.ndarray (n_samples, kde_size)
        y     — np.ndarray (n_samples,) — строковые метки типов решёток
        names — list[str] — имя структуры для каждого сэмпла
    """
    X, y, names = [], [], []
    skipped = []

    for struct_dir in sorted(kde_dir.iterdir()):
        if not struct_dir.is_dir():
            continue

        label = extract_label(struct_dir.name)
        if label is None:
            skipped.append(struct_dir.name)
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
                names.append(struct_dir.name)
                n_loaded += 1

        if verbose:
            print(f"  {struct_dir.name:40s}  [{label}]  {n_loaded} сэмплов")

    if skipped and verbose:
        print(f"\nПропущено (метка не определена): {', '.join(skipped)}")

    return np.array(X), np.array(y), names
