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
_DEFAULT_AUTOML_MODEL    = _ROOT / "ML" / "AutoML" / "extra_trees.pkl"

# ── v2: переобученные модели с правильным усреднением (200-dim, v3 PBC) ───────
_DEFAULT_RF_MODEL_V2        = _ROOT / "ML" / "rf_optimized_model_v2.pkl"
_DEFAULT_SUBSTANCE_MODEL_V2 = _ROOT / "ML" / "CatBoost" / "catboost_substance_v2.cbm"
_DEFAULT_AUTOML_MODEL_V2    = _ROOT / "ML" / "AutoML" / "extra_trees_v2.pkl"

# ── Кеш загруженных моделей (заполняется один раз, живёт весь процесс) ────────
_CACHED_CATBOOST:          object = None
_CACHED_CATBOOST_SUBSTANCE: object = None
_CACHED_RF:                object = None
_CACHED_AUTOML:            object = None


def _get_catboost_model():
    global _CACHED_CATBOOST
    if _CACHED_CATBOOST is None:
        _CACHED_CATBOOST = _load_model(_DEFAULT_MODEL)
    return _CACHED_CATBOOST


def _get_catboost_substance_model():
    global _CACHED_CATBOOST_SUBSTANCE
    if _CACHED_CATBOOST_SUBSTANCE is None:
        _CACHED_CATBOOST_SUBSTANCE = _load_model(_DEFAULT_SUBSTANCE_MODEL_V2)
    return _CACHED_CATBOOST_SUBSTANCE


def _get_rf_model():
    global _CACHED_RF
    if _CACHED_RF is None:
        _CACHED_RF = _load_sklearn_model(_DEFAULT_RF_MODEL_V2)
    return _CACHED_RF


def _get_automl_model():
    global _CACHED_AUTOML
    if _CACHED_AUTOML is None:
        _CACHED_AUTOML = _load_sklearn_model(_DEFAULT_AUTOML_MODEL)
    return _CACHED_AUTOML


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
    Используется для CatBoost, Random Forest и AutoML.

    Использует get_lattice_vectors3 — с периодическими граничными условиями (PBC),
    все ионы (без дедупликации). Соответствует pipeline обучения всех моделей
    (generate_dataset.py также использует v3).
    """
    try:
        from cris.core.spectrum import kde_array
        from cris.core.vectors import get_lattice_vectors3

        # Подавляем print()-вывод из get_lattice_vectors3
        _old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            vectors_dict = get_lattice_vectors3(normalized_coords)
        finally:
            sys.stdout = _old_stdout

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
    feat_vec: Optional[np.ndarray] = None,
) -> list[dict]:
    """
    Предсказывает тип решётки через CatBoost.
    Если feat_vec передан — пропускает вычисление дескриптора (быстрый путь).
    """
    model = _get_catboost_model()
    if model is None:
        return []

    feat = feat_vec if feat_vec is not None else _coords_to_feature_vector_200(normalized_coords)
    if feat is None:
        return []

    if len(feat) != len(model.feature_names_):
        logger.warning(
            "ml_predict: feature size mismatch (got {}, need {})",
            len(feat), len(model.feature_names_)
        )
        return []

    proba   = model.predict_proba(feat.reshape(1, -1))[0]
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
    model_path: Path = _DEFAULT_RF_MODEL_V2,
    top_k: int = 3,
    feat_vec: Optional[np.ndarray] = None,
) -> list[dict]:
    """
    Предсказывает класс через Random Forest (200-dim KDE вектор).
    Если feat_vec передан — пропускает вычисление дескриптора (быстрый путь).
    """
    model = _get_rf_model()
    if model is None:
        return []

    feat = feat_vec if feat_vec is not None else _coords_to_feature_vector_200(normalized_coords)
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
    model_path: Path = _DEFAULT_SUBSTANCE_MODEL_V2,
    top_k: int = 3,
    feat_vec: Optional[np.ndarray] = None,
) -> list[dict]:
    """
    Предсказывает конкретное вещество через CatBoost (200-dim KDE вектор).
    Если feat_vec передан — пропускает вычисление дескриптора (быстрый путь).
    """
    model = _get_catboost_substance_model()
    if model is None:
        return []

    feat = feat_vec if feat_vec is not None else _coords_to_feature_vector_200(normalized_coords)
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


def predict_automl(
    normalized_coords: list,
    model_path: Path = _DEFAULT_AUTOML_MODEL,
    top_k: int = 3,
    feat_vec: Optional[np.ndarray] = None,
) -> list[dict]:
    """
    Предсказывает конкретное вещество через AutoML (FLAML ExtraTrees, 200-dim KDE вектор).
    Если feat_vec передан — пропускает вычисление дескриптора (быстрый путь).
    """
    model = _get_automl_model()
    if model is None:
        return []

    feat = feat_vec if feat_vec is not None else _coords_to_feature_vector_200(normalized_coords)
    if feat is None:
        return []

    if len(feat) != model.n_features_in_:
        logger.warning(
            "ml_predict: AutoML feature size mismatch (got {}, need {})",
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

    logger.debug("AutoML prediction: top={} conf={}", results[0]["class"], results[0]["confidence"])
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
