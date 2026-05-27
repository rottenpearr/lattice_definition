"""
Предсказание типа кристаллической решётки через CatBoost + KDE-векторы.

Используется из main.py после coordinate-match, результат пишется
в recognition_result с method="CATBOOST".

Пример:
    from cris.core.ml_predict import predict_catboost
    results = predict_catboost(normalized_coords)
    # [{"class": "cubic_f", "lattice_type_id": 8, "confidence": 0.87}, ...]
"""
import io
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

import numpy as np
from scipy.stats import gaussian_kde

from cris.logger import logger

# ── Пути к моделям ────────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent.parent.parent
_DEFAULT_MODEL           = _ROOT / "ML" / "CatBoost" / "catboost_lattice.cbm"
_DEFAULT_RF_MODEL        = _ROOT / "ML" / "rf_optimized_model.pkl"
_DEFAULT_SUBSTANCE_MODEL = _ROOT / "ML" / "CatBoost" / "catboost_substance.cbm"

# ── Маппинг классов модели → name_en в таблице lattice_type ──────────────────
# Модель обучена на подтипах Браве-решётки; все cubic_* → "cubic" и т.д.
_CLASS_TO_LATTICE_EN: dict[str, str] = {
    "cubic_f":   "cubic",
    "cubic_i":   "cubic",
    "cubic_p":   "cubic",
    "hex_p":     "hexagonal",
    "trig_r":    "rhombohedral",
    "tetra_p":   "tetragonal",
    "tetra_i":   "tetragonal",
    "ortho_p":   "orthorhombic",
    "ortho_i":   "orthorhombic",
    "ortho_f":   "orthorhombic",
    "ortho_c":   "orthorhombic",
    "mono_p":    "monoclinic",
    "mono_c":    "monoclinic",
    "triclinic": "triclinic",
}


def _kde_array_1000(distances_counter: dict) -> np.ndarray:
    """KDE-вектор на сетке 1000 точек [0, 2] — формат, совместимый с моделью."""
    distances = []
    for dist, count in distances_counter.items():
        distances.extend([dist] * int(count))
    arr = np.array(distances, dtype=float)
    if len(arr) < 2:
        return np.zeros(1000)
    kde = gaussian_kde(arr, bw_method=0.1)
    x_grid = np.linspace(0, 2, 1000)
    return kde.evaluate(x_grid)


def _coords_to_feature_vector(normalized_coords: list) -> Optional[np.ndarray]:
    """
    Список [label, x, y, z] → усреднённый KDE-вектор 1000-dim.
    Подавляет print()-вывод из get_lattice_vectors3.
    """
    try:
        from cris.core.vectors import get_lattice_vectors3

        coords = normalized_coords
        if len(coords) < 30:
            coords = _expand_supercell(coords, n=2)

        _old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            vectors_dict = get_lattice_vectors3(coords)
        finally:
            sys.stdout = _old_stdout

        ion_arrays = []
        for distances in vectors_dict.values():
            counter = dict(Counter(distances))
            if len(counter) >= 2:
                arr = _kde_array_1000(counter)
                ion_arrays.append(arr)

        if not ion_arrays:
            return None
        return np.mean(ion_arrays, axis=0)
    except Exception as e:
        logger.warning("ml_predict: failed to compute feature vector: {}", e)
        return None


def _load_model(model_path: Path):
    """Ленивая загрузка CatBoost модели."""
    try:
        from catboost import CatBoostClassifier
        m = CatBoostClassifier()
        m.load_model(str(model_path))
        return m
    except ImportError:
        logger.warning("ml_predict: catboost not installed, skipping ML prediction")
        return None
    except Exception as e:
        logger.warning("ml_predict: cannot load model {}: {}", model_path, e)
        return None


def _load_sklearn_model(model_path: Path):
    """Ленивая загрузка sklearn модели через joblib."""
    try:
        import joblib
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return joblib.load(str(model_path))
    except ImportError:
        logger.warning("ml_predict: joblib not installed")
        return None
    except Exception as e:
        logger.warning("ml_predict: cannot load sklearn model {}: {}", model_path, e)
        return None



def _coords_to_feature_vector_200(normalized_coords: list) -> Optional[np.ndarray]:
    """
    Список [label, x, y, z] → усреднённый KDE-вектор 200-dim.
    Используется для CatBoost и Random Forest.

    Использует get_lattice_vectors2 — без PBC, только уникальные позиции ионов.
    Это соответствует pipeline обучения обеих моделей (spectrum.py тоже использует v2).
    """
    try:
        from cris.core.spectrum import kde_array
        from cris.core.vectors import get_lattice_vectors2

        vectors_dict = get_lattice_vectors2(normalized_coords)

        ion_arrays = []
        for distances in vectors_dict.values():
            counter = dict(Counter(distances))
            try:
                arr = kde_array(counter)
            except Exception:
                arr = np.zeros(200)
            ion_arrays.append(arr)

        if not ion_arrays:
            return None
        return np.mean(ion_arrays, axis=0)
    except Exception as e:
        logger.warning("ml_predict: failed to compute 200-dim feature vector: {}", e)
        return None


def predict_catboost(
    normalized_coords: list,
    model_path: Path = _DEFAULT_MODEL,
    top_k: int = 3,
) -> list[dict]:
    """
    Предсказывает тип решётки через CatBoost.

    Args:
        normalized_coords: список [label, x, y, z] — уже нормализованные
        model_path:        путь к .cbm файлу
        top_k:             сколько топ-классов вернуть

    Returns:
        Список словарей (отсортированных по убыванию confidence):
        [{"class": "cubic_f", "lattice_name": "cubic",
          "lattice_type_id": None, "confidence": 0.87}, ...]
        lattice_type_id заполняется отдельно через resolve_lattice_ids().
    """
    if not model_path.exists():
        logger.debug("ml_predict: model file not found: {}", model_path)
        return []

    model = _load_model(model_path)
    if model is None:
        return []

    feat = _coords_to_feature_vector_200(normalized_coords)
    if feat is None:
        return []

    if len(feat) != len(model.feature_names_):
        logger.warning(
            "ml_predict: feature size mismatch (got {}, need {})",
            len(feat), len(model.feature_names_)
        )
        return []

    proba  = model.predict_proba(feat.reshape(1, -1))[0]
    classes = model.classes_

    top_indices = np.argsort(proba)[::-1][:top_k]
    results = []
    for i in top_indices:
        cls_name = classes[i]
        results.append({
            "class":           cls_name,
            "lattice_name":    _CLASS_TO_LATTICE_EN.get(cls_name, cls_name),
            "lattice_type_id": None,
            "confidence":      round(float(proba[i]), 4),
        })

    logger.debug("CatBoost prediction: top={} conf={}", results[0]["class"], results[0]["confidence"])
    return results


def predict_rf(
    normalized_coords: list,
    model_path: Path = _DEFAULT_RF_MODEL,
    top_k: int = 3,
) -> list[dict]:
    """
    Предсказывает класс через Random Forest (200-dim KDE вектор).

    Args:
        normalized_coords: список [label, x, y, z] — уже нормализованные
        model_path:        путь к .pkl файлу
        top_k:             сколько топ-классов вернуть

    Returns:
        [{"class": "UC2_phase1", "lattice_name": "UC2_phase1",
          "lattice_type_id": None, "confidence": 0.52}, ...]
    """
    if not model_path.exists():
        logger.debug("ml_predict: RF model not found: {}", model_path)
        return []

    model = _load_sklearn_model(model_path)
    if model is None:
        return []

    feat = _coords_to_feature_vector_200(normalized_coords)
    if feat is None:
        return []

    if len(feat) != model.n_features_in_:
        logger.warning(
            "ml_predict: RF feature size mismatch (got {}, need {})",
            len(feat), model.n_features_in_,
        )
        return []

    proba   = model.predict_proba(feat.reshape(1, -1))[0]
    classes = model.classes_

    top_indices = np.argsort(proba)[::-1][:top_k]
    results = [
        {
            "class":           str(classes[i]),
            "lattice_name":    _CLASS_TO_LATTICE_EN.get(str(classes[i]), str(classes[i])),
            "lattice_type_id": None,
            "confidence":      round(float(proba[i]), 4),
        }
        for i in top_indices
    ]

    logger.debug("RF prediction: top={} conf={}", results[0]["class"], results[0]["confidence"])
    return results


def predict_catboost_substance(
    normalized_coords: list,
    model_path: Path = _DEFAULT_SUBSTANCE_MODEL,
    top_k: int = 3,
) -> list[dict]:
    """
    Предсказывает конкретное вещество через CatBoost (200-dim KDE вектор).
    Модель обучается скриптом ML/CatBoost/train_substance.py на тех же данных,
    что и RF (urановые соединения: UC, UN2, UC2_phase1 и т.д.).

    Returns:
        [{"class": "UC", "lattice_name": "UC",
          "lattice_type_id": None, "confidence": 0.85}, ...]
    """
    if not model_path.exists():
        logger.debug("ml_predict: substance model not found: {}", model_path)
        return []

    model = _load_model(model_path)
    if model is None:
        return []

    feat = _coords_to_feature_vector_200(normalized_coords)
    if feat is None:
        return []

    if len(feat) != len(model.feature_names_):
        logger.warning(
            "ml_predict: substance model feature size mismatch (got {}, need {})",
            len(feat), len(model.feature_names_)
        )
        return []

    proba   = model.predict_proba(feat.reshape(1, -1))[0]
    classes = model.classes_

    top_indices = np.argsort(proba)[::-1][:top_k]
    results = []
    for i in top_indices:
        cls_name = str(classes[i])
        results.append({
            "class":           cls_name,
            "lattice_name":    _CLASS_TO_LATTICE_EN.get(cls_name, cls_name),
            "lattice_type_id": None,
            "confidence":      round(float(proba[i]), 4),
        })

    logger.debug("CatBoost-substance prediction: top={} conf={}", results[0]["class"], results[0]["confidence"])
    return results


def resolve_lattice_ids(predictions: list[dict]) -> list[dict]:
    """
    Заполняет lattice_type_id в каждом предсказании,
    делая один запрос к БД для уникальных имён.
    """
    if not predictions:
        return predictions

    from cris.db.connection import get_cursor

    unique_names = {p["lattice_name"] for p in predictions}
    name_to_id: dict[str, int] = {}
    try:
        with get_cursor() as cur:
            for name in unique_names:
                cur.execute(
                    "SELECT id FROM lattice_type WHERE name_en = %s LIMIT 1",
                    (name,)
                )
                row = cur.fetchone()
                if row:
                    name_to_id[name] = row[0]
    except Exception as e:
        logger.warning("resolve_lattice_ids failed: {}", e)

    for p in predictions:
        p["lattice_type_id"] = name_to_id.get(p["lattice_name"])

    return predictions
