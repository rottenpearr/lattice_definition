# ============================================================
# Ячейка 1 — установка зависимостей
# ============================================================
# !pip install catboost -q


# ============================================================
# Ячейка 2 — монтирование Drive и распаковка
# ============================================================
# from google.colab import drive
# drive.mount('/content/drive')
#
# import zipfile
# with zipfile.ZipFile('/content/drive/MyDrive/dataset_full.zip', 'r') as z:
#     z.extractall('/content/dataset')
# print("Готово")


# ============================================================
# Ячейка 3 — обучение (вставь и запусти целиком)
# ============================================================

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import classification_report
from catboost import CatBoostClassifier
import joblib

# --- Загрузка датасета (тот же формат что RF) ---
def load_and_average_data(base_dir):
    X, y = [], []
    for label in os.listdir(base_dir):
        label_dir = os.path.join(base_dir, label)
        if not os.path.isdir(label_dir):
            continue
        for sample_dir in os.listdir(label_dir):
            sample_path = os.path.join(label_dir, sample_dir)
            if not os.path.isdir(sample_path):
                continue
            sample_kdes = []
            for filename in os.listdir(sample_path):
                if filename.endswith('.csv'):
                    filepath = os.path.join(sample_path, filename)
                    kde_values = pd.read_csv(filepath, header=0).values.astype(np.float32).flatten()
                    sample_kdes.append(kde_values)
            if sample_kdes:
                V_mean = np.mean(sample_kdes, axis=0)
                X.append(V_mean)
                y.append(label)
    return np.array(X, dtype=np.float32), np.array(y)

# Путь к распакованному датасету
# Если в zip есть вложенная папка 'dataset' — укажи '/content/dataset/dataset'
DATASET_DIR = '/content/dataset'

X, y = load_and_average_data(DATASET_DIR)
print(f"Сэмплов: {X.shape[0]}, признаков: {X.shape[1]}")
print(f"Классы: {sorted(set(y))}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# --- CatBoost ---
print("\n=== CatBoost ===")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

model = CatBoostClassifier(
    iterations=500,
    depth=6,
    learning_rate=0.1,
    loss_function='MultiClass',
    eval_metric='Accuracy',
    verbose=100,
    random_seed=42,
)
model.fit(X_train, y_train, eval_set=(X_test, y_test))

y_pred = model.predict(X_test).flatten()
print(classification_report(y_test, y_pred))

model.save_model('/content/catboost_substance.cbm')
print("Модель сохранена: /content/catboost_substance.cbm")


# ============================================================
# Ячейка 4 — скачать модель
# ============================================================
# from google.colab import files
# files.download('/content/catboost_substance.cbm')
