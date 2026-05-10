"""
Обучение CatBoost-классификатора типов кристаллических решёток.

Запуск:
    python ML/catboost/train.py
    python ML/catboost/train.py --kde-dir data/kde_arrays/macro
    python ML/catboost/train.py --iterations 1000 --depth 8
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_dataset

MODEL_OUT = Path(__file__).parent / "catboost_lattice.cbm"


def train(kde_dir: Path, iterations: int, depth: int, lr: float, test_size: float):
    print(f"\nЗагрузка датасета из: {kde_dir}\n")
    X, y, _ = load_dataset(kde_dir)

    if len(X) == 0:
        print("Датасет пуст. Сначала запустите generate_all_datasets.py")
        sys.exit(1)

    classes = sorted(set(y))
    print(f"\nКлассов: {len(classes)}  —  {classes}")
    print(f"Сэмплов: {len(X)}  (вектор: {X.shape[1]} признаков)")

    # Распределение по классам
    print("\nРаспределение:")
    for cls in classes:
        n = np.sum(y == cls)
        print(f"  {cls:15s}  {n}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=42
    )
    print(f"\nTrain: {len(X_train)}  |  Test: {len(X_test)}")

    model = CatBoostClassifier(
        iterations=iterations,
        depth=depth,
        learning_rate=lr,
        loss_function="MultiClass",
        eval_metric="Accuracy",
        verbose=100,
        random_seed=42,
    )

    print("\nОбучение...\n")
    model.fit(X_train, y_train, eval_set=(X_test, y_test))

    y_pred = model.predict(X_test).flatten()
    print("\n" + "=" * 55)
    print(classification_report(y_test, y_pred))

    # Матрица ошибок
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    print("Матрица ошибок (строки=факт, столбцы=предсказание):")
    header = "".join(f"{c[:7]:>8}" for c in classes)
    print(f"{'':15}{header}")
    for i, cls in enumerate(classes):
        row = "".join(f"{cm[i][j]:>8}" for j in range(len(classes)))
        print(f"  {cls:13}{row}")

    model.save_model(str(MODEL_OUT))
    print(f"\nМодель сохранена: {MODEL_OUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Обучение CatBoost на KDE-датасете")
    parser.add_argument("--kde-dir", type=Path,
                        default=ROOT / "data" / "kde_arrays" / "macro",
                        help="Папка с KDE-массивами")
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--depth",      type=int, default=6)
    parser.add_argument("--lr",         type=float, default=0.1)
    parser.add_argument("--test-size",  type=float, default=0.2)
    args = parser.parse_args()

    train(args.kde_dir, args.iterations, args.depth, args.lr, args.test_size)
