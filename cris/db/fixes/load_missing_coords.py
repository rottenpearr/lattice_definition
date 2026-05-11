"""
Утилита: заполняет поле xyz_path в reference_structure для структур, у которых оно пустое.

Что делает скрипт:
  1. Находит все reference_structure, у которых xyz_path IS NULL или пустой
  2. Для каждой такой структуры ищет подходящий XYZ-файл по формуле или имени
  3. Обновляет xyz_path в reference_structure

Маппинг XYZ-файлов задан в FORMULA_TO_XYZ (приоритет по формуле).
Если формула не совпала — пробуем по имени через NAME_KEYWORDS_TO_XYZ.

ВАЖНО: скрипт использует 5x5x5 суперъячейки из data/structures/macro/source/.

Запуск:
    python -m cris.db.fixes.load_missing_coords            # обновить всё
    python -m cris.db.fixes.load_missing_coords --dry-run  # только показать план
    python -m cris.db.fixes.load_missing_coords --id=5     # только одну структуру
"""
import sys
from pathlib import Path

import psycopg2

from cris.db.config import db_config
from cris.logger import logger

# ── Пути ─────────────────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent.parent.parent.parent  # корень проекта
_MACRO_DIR = _ROOT / "data" / "structures" / "macro" / "source"

# ── Маппинг: нормализованная формула → XYZ-файл ──────────────────────────────
# Ключ: formula.replace(" ", "").upper()
FORMULA_TO_XYZ: dict[str, str | None] = {
    # Элементы
    "AL":    "Al.xyz",          # FCC
    "BI":    "trig_r_Bi.xyz",   # Rhombohedral
    "CU":    "Cu.xyz",          # FCC
    "FE":    "Fe.xyz",          # BCC
    "IN":    "tetra_i_In.xyz",  # Tetragonal I
    "NI":    "Cu.xyz",          # FCC — та же нормализованная структура что и Cu
    "S":     "ortho_f_S.xyz",   # Orthorhombic F
    "SE":    "mono_p_Se.xyz",   # Monoclinic P
    "SN":    "tetra_p_Sn.xyz",  # Tetragonal P
    "TI":    "hex_p_Ti.xyz",    # Hexagonal P
    "U":     "ortho_p_U.xyz",   # Orthorhombic P (alpha-U)
    "W":     "Fe.xyz",          # BCC — та же структура что и Fe
    "ZN":    "hex_p_Zn.xyz",    # Hexagonal P
    # Бинарные соединения
    "CSCL":  "CsCl.xyz",        # Cubic SC (2-atom basis)
    "CLCS":  "CsCl.xyz",
    "NACL":  "NaCl.xyz",        # Cubic FCC (2-atom basis)
    "CLNA":  "NaCl.xyz",
    "UC":    "UC.xyz",          # NaCl-type cubic
    "UN":    "UN.xyz",          # NaCl-type cubic
    # Структуры без подходящего XYZ — явно None (пропускаем)
    "UO2":   None,   # Fluorite cubic — нет XYZ с правильной структурой
    "PUO2":  None,   # Fluorite cubic
    "THO2":  None,   # Fluorite cubic
    "MGO":   None,   # Покрыт COD id=25
    "SI":    None,   # Diamond cubic — особая структура
    "GE":    None,   # Diamond cubic
    "GAAS":  None,   # Zincblende — нет XYZ
    "ZNS":   None,   # Zincblende — hex_p_Zn.xyz неверен (другая структура)
    "AL2O3": None,   # Trigonal corundum — нет XYZ
    "ZRO2":  None,   # Orthorhombic — нет подходящего XYZ
}

# Дополнительный маппинг по ключевым словам из name.
# ВАЖНО: более специфичные ключи должны стоять РАНЬШЕ общих.
NAME_KEYWORDS_TO_XYZ: list[tuple[str, str]] = [
    # Конкретные соединения — первыми, чтобы не перебивались общими
    ("sodium chloride",   "NaCl.xyz"),
    ("caesium chloride",  "CsCl.xyz"),
    ("cesium chloride",   "CsCl.xyz"),
    ("uranium carbide",   "UC.xyz"),
    ("uranium nitride",   "UN.xyz"),
    # Чистые элементы
    ("iron",              "Fe.xyz"),
    ("tungsten",          "Fe.xyz"),   # BCC, как Fe
    ("aluminium",         "Al.xyz"),
    ("aluminum",          "Al.xyz"),
    ("copper",            "Cu.xyz"),
    ("nickel",            "Cu.xyz"),   # FCC, как Cu
    ("titanium",          "hex_p_Ti.xyz"),
    ("zinc metal",        "hex_p_Zn.xyz"),   # только чистый цинк, не соединения
    ("selenium",          "mono_p_Se.xyz"),
    ("sulfur",            "ortho_f_S.xyz"),
    ("sulphur",           "ortho_f_S.xyz"),
    ("indium",            "tetra_i_In.xyz"),
    ("tin",               "tetra_p_Sn.xyz"),
    ("bismuth",           "trig_r_Bi.xyz"),
]


def _find_xyz(formula: str, name: str) -> Path | None:
    """Ищет XYZ-файл по формуле, затем по имени."""
    norm_formula = formula.replace(" ", "").upper() if formula else ""

    # 1. Прямое совпадение по формуле
    if norm_formula in FORMULA_TO_XYZ:
        filename = FORMULA_TO_XYZ[norm_formula]
        if filename is None:
            return None   # явно помечен как «нет XYZ»
        path = _MACRO_DIR / filename
        if path.exists():
            return path
        logger.warning("  XYZ file mapped but not found: {}", path)

    # 2. Поиск по ключевым словам в имени
    name_lower = (name or "").lower()
    for keyword, filename in NAME_KEYWORDS_TO_XYZ:
        if keyword in name_lower:
            path = _MACRO_DIR / filename
            if path.exists():
                return path

    return None


def load_missing_coords(dry_run: bool = False, only_id: int | None = None) -> None:
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    try:
        # ── 1. Находим структуры без xyz_path ───────────────────────────
        if only_id:
            cur.execute("""
                SELECT rs.id, rs.formula, rs.name, rs.lattice_type_id
                FROM reference_structure rs
                WHERE rs.id = %s
                  AND (rs.xyz_path IS NULL OR rs.xyz_path = '')
            """, (only_id,))
        else:
            cur.execute("""
                SELECT rs.id, rs.formula, rs.name, rs.lattice_type_id
                FROM reference_structure rs
                WHERE rs.xyz_path IS NULL OR rs.xyz_path = ''
                ORDER BY rs.id
            """)
        missing = cur.fetchall()

        if not missing:
            logger.info("No structures without xyz_path found{}",
                        f" (id={only_id})" if only_id else "")
            return

        logger.info("Found {} structure(s) without xyz_path:", len(missing))

        loaded = []
        skipped = []

        for struct_id, formula, name, lt_id in missing:
            xyz_path = _find_xyz(formula or "", name or "")

            if xyz_path is None:
                skipped.append((struct_id, formula, name))
                logger.warning(
                    "  SKIP id={} '{}' formula='{}' — no XYZ file found",
                    struct_id, name, formula
                )
                continue

            logger.info(
                "  LOAD id={} '{}' (formula='{}') ← {}",
                struct_id, name, formula, xyz_path.name
            )

            if dry_run:
                loaded.append((struct_id, formula, name, xyz_path.name))
                continue

            # ── 2. Обновляем xyz_path в reference_structure ──────────────
            try:
                rel_path = str(xyz_path.relative_to(_ROOT)).replace("\\", "/")
                cur.execute(
                    "UPDATE reference_structure SET xyz_path = %s WHERE id = %s",
                    (rel_path, struct_id)
                )
                loaded.append((struct_id, formula, name, xyz_path.name))
                logger.info("    Updated xyz_path={} for structure_id={}", rel_path, struct_id)
            except Exception as e:
                logger.error("    Failed for id={}: {}", struct_id, e)
                skipped.append((struct_id, formula, name))

        # ── 3. Итог ──────────────────────────────────────────────────────
        if not dry_run:
            conn.commit()

        status = "[DRY RUN] " if dry_run else ""
        logger.info(
            "{}load_missing_coords: loaded={}, skipped={}",
            status, len(loaded), len(skipped)
        )
        if skipped:
            logger.warning(
                "Skipped (no XYZ): {}",
                [(sid, f) for sid, f, _ in skipped]
            )

    except Exception as e:
        conn.rollback()
        logger.error("load_missing_coords failed: {}", e)
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    dry  = "--dry-run" in sys.argv
    only = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--id=")), None)
    load_missing_coords(dry_run=dry, only_id=only)
