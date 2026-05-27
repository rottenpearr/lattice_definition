"""
cris-core — Crystal Recognition & Identification System

Быстрый старт (ML-методы, без БД):
    from cris import identify

    result = identify([
        {"label": "U", "x": 0.0, "y": 0.0, "z": 0.0},
        {"label": "U", "x": 0.5, "y": 0.5, "z": 0.0},
        {"label": "U", "x": 0.5, "y": 0.0, "z": 0.5},
        {"label": "U", "x": 0.0, "y": 0.5, "z": 0.5},
        {"label": "N", "x": 0.5, "y": 0.5, "z": 0.5},
        {"label": "N", "x": 0.0, "y": 0.0, "z": 0.5},
        {"label": "N", "x": 0.0, "y": 0.5, "z": 0.0},
        {"label": "N", "x": 0.5, "y": 0.0, "z": 0.0},
    ])

    print(result.lattice_type)         # 'cubic'
    print(result.substance)            # 'UN'
    print(result.lattice_confidence)   # 0.87

С поиском по базе данных (требует PostgreSQL + .env):
    result = identify(sites, methods=["catboost", "catboost_substance", "rf", "db"])
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

__version__ = "0.4.3"
__all__ = ["identify", "CrisResult"]


@dataclass
class CrisResult:
    """Результат распознавания кристаллической решётки."""

    # Тип решётки — лучшее предсказание CatBoost
    lattice_type: Optional[str] = None
    lattice_confidence: Optional[float] = None

    # Вещество — лучшее предсказание (catboost_substance, затем rf)
    substance: Optional[str] = None
    substance_confidence: Optional[float] = None

    # Совпадение по базе данных (только при methods=["db"])
    db_match_name: Optional[str] = None
    db_match_formula: Optional[str] = None
    db_match_probability: Optional[float] = None

    # Полные предсказания по каждому методу
    ml_results: list[dict] = field(default_factory=list)

    # Нормализованные входные координаты [[label, x, y, z], ...]
    normalized_coords: list = field(default_factory=list)

    def __repr__(self) -> str:
        parts = []
        if self.lattice_type:
            conf = f"{self.lattice_confidence:.0%}" if self.lattice_confidence is not None else "?"
            parts.append(f"lattice={self.lattice_type!r} ({conf})")
        if self.substance:
            conf = f"{self.substance_confidence:.0%}" if self.substance_confidence is not None else "?"
            parts.append(f"substance={self.substance!r} ({conf})")
        if self.db_match_name:
            parts.append(f"db={self.db_match_name!r}")
        return f"CrisResult({', '.join(parts) or 'no prediction'})"


def identify(
    sites: list,
    methods: list[str] | None = None,
) -> CrisResult:
    """
    Определяет тип кристаллической решётки по координатам ионов.

    Args:
        sites:   список ионов. Каждый ион можно задать как:
                   - dict:       {"label": "U", "x": 0.0, "y": 0.0, "z": 0.0}
                   - list/tuple: ["U", 0.0, 0.0, 0.0]
                 Координаты могут быть дробными (фракционными) или декартовыми —
                 нормализация в куб [0, 1] выполняется автоматически.

        methods: список методов распознавания. По умолчанию все ML-методы:
                   ["catboost", "catboost_substance", "rf"]
                 Доступные значения:
                   "catboost"           — тип решётки (CatBoost, 14 классов Браве)
                   "catboost_substance" — вещество (CatBoost)
                   "rf"                 — вещество (Random Forest)
                   "db"                 — геометрический поиск по эталонной БД
                                          (требует PostgreSQL и .env с DB_*)

    Returns:
        CrisResult: объект с полями lattice_type, substance, confidence и т.д.

    Examples:
        >>> from cris import identify
        >>> result = identify([["U", 0, 0, 0], ["N", 0.5, 0.5, 0.5]])
        >>> result.lattice_type
        'cubic'

        >>> # только ML, без DB
        >>> result = identify(sites, methods=["catboost", "rf"])

        >>> # с поиском в базе
        >>> result = identify(sites, methods=["catboost", "rf", "db"])
    """
    if methods is None:
        methods = ["catboost", "catboost_substance", "rf"]

    # ── Нормализация входных данных ───────────────────────────────────────────
    from cris.core.coordinates import shift_coordinates, normalize_coordinates

    raw: list[list] = []
    for s in sites:
        if isinstance(s, dict):
            raw.append([s["label"], float(s["x"]), float(s["y"]), float(s["z"])])
        else:
            raw.append([str(s[0]), float(s[1]), float(s[2]), float(s[3])])

    shifted    = shift_coordinates(raw)
    normalized = normalize_coordinates(shifted)

    result = CrisResult(normalized_coords=normalized)

    # ── ML-методы ────────────────────────────────────────────────────────────
    if any(m in methods for m in ("catboost", "catboost_substance", "rf")):
        from cris.core.ml_predict import (
            predict_catboost,
            predict_catboost_substance,
            predict_rf,
        )

        if "catboost" in methods:
            preds = predict_catboost(normalized)
            if preds:
                best = preds[0]
                result.lattice_type       = best["lattice_name"]
                result.lattice_confidence = best["confidence"]
            result.ml_results.append({"method": "catboost", "predictions": preds})

        if "catboost_substance" in methods:
            preds = predict_catboost_substance(normalized)
            if preds:
                best = preds[0]
                result.substance            = best["class"]
                result.substance_confidence = best["confidence"]
            result.ml_results.append({"method": "catboost_substance", "predictions": preds})

        if "rf" in methods:
            preds = predict_rf(normalized)
            # rf заполняет вещество только если catboost_substance не дал результата
            if preds and result.substance is None:
                best = preds[0]
                result.substance            = best["class"]
                result.substance_confidence = best["confidence"]
            result.ml_results.append({"method": "rf", "predictions": preds})

    # ── Геометрический поиск по БД ───────────────────────────────────────────
    if "db" in methods:
        try:
            from cris.db.queries import check_coords
            coords_dict = {i: row for i, row in enumerate(normalized)}
            db_result   = check_coords(coords_dict, len(sites))
            if db_result is not False:
                _names, top_lattice, top_struct = db_result
                if isinstance(top_struct, (list, tuple)) and len(top_struct) >= 2:
                    struct_info, prob = top_struct[0], top_struct[1]
                    if isinstance(struct_info, dict):
                        result.db_match_name    = struct_info.get("name")
                        result.db_match_formula = struct_info.get("formula")
                    else:
                        result.db_match_name = str(struct_info)
                    result.db_match_probability = float(prob) if prob is not None else None
        except Exception as exc:
            from cris.logger import logger
            logger.warning("identify: db method failed: {}", exc)

    return result
