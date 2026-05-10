"""
Предсказание типа решётки по XYZ-файлу с помощью обученного CatBoost.

Запуск:
    python ML/catboost/predict.py path/to/structure.xyz
    python ML/catboost/predict.py path/to/structure.xyz --model ML/catboost/catboost_lattice.cbm
    python ML/catboost/predict.py path/to/structure.xyz --noise 2
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from cris.tools.testing import xyz_to_normalized_coords_with_noise
from cris.core.vectors import get_lattice_vectors3
from cris.core.spectrum import kde_array

DEFAULT_MODEL = Path(__file__).parent / "catboost_lattice.cbm"


def xyz_to_feature_vector(xyz_path: str, noise_percent: float = 0.0, seed: int = 42) -> np.ndarray:
    """XYZ → усреднённый KDE-вектор (такой же формат, как при обучении)."""
    coords = xyz_to_normalized_coords_with_noise(xyz_path, noise_percent=noise_percent, seed=seed)
    vectors_dict = get_lattice_vectors3(coords)

    ion_arrays = []
    for distances in vectors_dict.values():
        arr = kde_array(dict(Counter(distances)))
        ion_arrays.append(arr)

    if not ion_arrays:
        raise ValueError(f"Не удалось извлечь векторы из {xyz_path}")

    return np.mean(ion_arrays, axis=0)


def predict(xyz_path: str, model_path: Path, noise_percent: float, top_k: int):
    if not model_path.exists():
        print(f"Модель не найдена: {model_path}")
        print("Сначала запустите: python ML/catboost/train.py")
        sys.exit(1)

    model = CatBoostClassifier()
    model.load_model(str(model_path))

    print(f"Файл  : {xyz_path}")
    print(f"Модель: {model_path}\n")

    vec = xyz_to_feature_vector(xyz_path, noise_percent=noise_percent)
    X = vec.reshape(1, -1)

    pred_label = model.predict(X)[0][0]
    proba = model.predict_proba(X)[0]
    classes = model.classes_

    # Топ-K предсказаний
    top_indices = np.argsort(proba)[::-1][:top_k]
    print(f"Предсказание: {pred_label}\n")
    print(f"Топ-{top_k} вероятностей:")
    for i in top_indices:
        bar = "█" * int(proba[i] * 30)
        print(f"  {classes[i]:15s}  {proba[i]:.3f}  {bar}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Предсказание типа решётки по XYZ")
    parser.add_argument("xyz", type=str, help="Путь к XYZ-файлу")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--noise", type=float, default=0.0, help="Шум при извлечении KDE, %% от a")
    parser.add_argument("--top",   type=int,   default=5,   help="Сколько топ-классов показать")
    args = parser.parse_args()

    predict(args.xyz, args.model, args.noise, args.top)
