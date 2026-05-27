"""
Обучение CatBoost-классификатора конкретных веществ (UC, UN2, UC2_phase1 и т.д.).

Читает датасет НАПРЯМУЮ из zip-архива, без распаковки на диск.

Ожидаемая структура внутри zip:
    <любая_корневая_папка>/
        UC/
            sample_001/
                ion_U.csv
                ion_C.csv
                ...
            sample_002/
                ...
        UN2/
            ...

Каждый CSV содержит столбец kde_values (200 значений).
Ионы внутри одного sample усредняются → один вектор 200-dim.

Запуск:
    python ML/CatBoost/train_substance.py
    python ML/CatBoost/train_substance.py --zip ML/dataset_full.zip
    python ML/CatBoost/train_substance.py --zip ML/dataset_full.zip --iterations 500
"""

import argparse
import io
import sys
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

ROOT     = Path(__file__).parent.parent.parent
ZIP_DEFAULT = Path(__file__).parent.parent / "dataset_full.zip"
MODEL_OUT   = Path(__file__).parent / "catboost_substance.cbm"


def load_dataset_from_zip(zip_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """
    Читает датасет прямо из zip-архива без распаковки.

    Структура: <root>/<label>/<sample>/<ion>.csv
    Возвращает X (n_samples, kde_size) и y (n_samples,).
    """
    print(f"Открываю архив: {zip_path}\n")

    # Собираем структуру: {(label, sample_id): [kde_array, ...]}
    samples: dict[tuple, list[np.ndarray]] = defaultdict(list)

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        csv_files = [n for n in names if n.endswith(".csv")]
        print(f"CSV-файлов в архиве: {len(csv_files)}")

        for entry in csv_files:
            parts = PurePosixPath(entry).parts
            # Ожидаем минимум 3 уровня: label/sample/ion.csv
            # (возможен дополнительный корневой уровень: root/label/sample/ion.csv)
            if len(parts) < 3:
                continue

            # Пропускаем корневую папку если она есть
            if len(parts) == 4:
                _, label, sample, _ = parts
            elif len(parts) == 3:
                label, sample, _ = parts
            else:
                continue

            try:
                with zf.open(entry) as f:
                    df = pd.read_csv(io.TextIOWrapper(f, encoding="utf-8"))

                if "kde_values" in df.columns:
                    arr = df["kde_values"].values.astype(np.float32)
                else:
                    arr = df.iloc[:, 0].values.astype(np.float32)

                samples[(label, sample)].append(arr)
            except Exception:
                continue

    if not samples:
        raise ValueError("Не найдено ни одного валидного sample в архиве. Проверьте структуру zip.")

    X, y = [], []
    label_counts: dict[str, int] = defaultdict(int)

    for (label, _sample), ion_arrays in samples.items():
        V_mean = np.mean(ion_arrays, axis=0)
        X.append(V_mean)
        y.append(label)
        label_counts[label] += 1

    print("\nРаспределение по классам:")
    for lbl, cnt in sorted(label_counts.items()):
        print(f"  {lbl:25s}  {cnt} сэмплов")

    return np.array(X, dtype=np.float32), np.array(y)


def train(zip_path: Path, iterations: int, depth: int, lr: float, test_size: float):
    X, y = load_dataset_from_zip(zip_path)

    if len(X) == 0:
        print("\nДатасет пуст.")
        sys.exit(1)

    classes = sorted(set(y))
    print(f"\nКлассов: {len(classes)}  —  {classes}")
    print(f"Всего сэмплов: {len(X)}  (размерность вектора: {X.shape[1]})")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=42
    )
    print(f"\nTrain: {len(X_train)}  |  Test: {len(X_test)}")

    # 5-фолдовая кросс-валидация
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    model_cv = CatBoostClassifier(
        iterations=iterations, depth=depth, learning_rate=lr,
        loss_function="MultiClass", eval_metric="Accuracy",
        verbose=0, random_seed=42,
    )
    print("\nКросс-валидация (5 фолдов)...")
    cv_scores = cross_val_score(model_cv, X_train, y_train, cv=cv, scoring="accuracy")
    print(f"  Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Финальное обучение
    model = CatBoostClassifier(
        iterations=iterations, depth=depth, learning_rate=lr,
        loss_function="MultiClass", eval_metric="Accuracy",
        verbose=100, random_seed=42,
    )
    print("\nОбучение финальной модели...\n")
    model.fit(X_train, y_train, eval_set=(X_test, y_test))

    y_pred = model.predict(X_test).flatten()
    print("\n" + "=" * 60)
    print(classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred, labels=classes)
    print("Матрица ошибок (строки=факт, столбцы=предсказание):")
    header = "".join(f"{c[:8]:>10}" for c in classes)
    print(f"{'':22}{header}")
    for i, cls in enumerate(classes):
        row = "".join(f"{cm[i][j]:>10}" for j in range(len(classes)))
        print(f"  {cls:20}{row}")

    model.save_model(str(MODEL_OUT))
    print(f"\nМодель сохранена: {MODEL_OUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Обучение CatBoost на классах веществ из zip-архива")
    parser.add_argument(
        "--zip", type=Path,
        default=ZIP_DEFAULT,
        help=f"Путь к zip-архиву (по умолчанию: {ZIP_DEFAULT})"
    )
    parser.add_argument("--iterations", type=int,   default=500)
    parser.add_argument("--depth",      type=int,   default=6)
    parser.add_argument("--lr",         type=float, default=0.1)
    parser.add_argument("--test-size",  type=float, default=0.2)
    args = parser.parse_args()

    if not args.zip.exists():
        print(f"Архив не найден: {args.zip}")
        sys.exit(1)

    train(args.zip, args.iterations, args.depth, args.lr, args.test_size)
