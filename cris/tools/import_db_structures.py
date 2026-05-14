"""
Пакетный импорт структур из data/db/ в PostgreSQL.

Для каждого JSON:
  1. json_to_db  → reference_structure + structure_site (метаданные и символы)
  2. xyz_to_db   → structure_site (координаты, если есть XYZ с таким же именем)

Запуск:
    python -m cris.tools.import_db_structures
"""
import json
import sys
from pathlib import Path

import psycopg2

from cris.db.config import db_config
from cris.db.importers.json_to_db import insert_data
from cris.db.importers.xyz_to_db import parse_xyz, upsert_sites
from cris.core.coordinates import shift_coordinates, normalize_coordinates
from cris.logger import logger

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "db"
JSON_DIR = DATA_DIR / "json"
XYZ_DIR  = DATA_DIR / "xyz"


def import_all() -> None:
    json_files = sorted(JSON_DIR.glob("*.json"))
    if not json_files:
        logger.error("No JSON files found in {}", JSON_DIR)
        sys.exit(1)

    logger.info("Found {} JSON files to import", len(json_files))

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    imported = 0
    skipped  = 0
    errors   = 0

    for jf in json_files:
        stem = jf.stem  # e.g. "1000041"
        try:
            with open(jf, encoding="utf-8") as f:
                data = json.load(f)

            lt_id, struct_id = insert_data(cursor, data)
            conn.commit()

            # XYZ — только для справки, координаты читаются из файлов напрямую queries.py
            xyz_candidates = list(XYZ_DIR.glob(f"{stem}.xyz")) + list(XYZ_DIR.glob(f"{stem}_*.xyz"))
            xyz_note = f" xyz={xyz_candidates[0].name}" if xyz_candidates else " (no XYZ)"
            logger.info("  ✓ {} → structure_id={} lt={}{}", stem, struct_id, lt_id, xyz_note)

            imported += 1

        except Exception as e:
            conn.rollback()
            # Если структура уже была — это не ошибка
            if "already" in str(e).lower() or struct_id:
                skipped += 1
                logger.debug("  = {} skipped ({})", stem, str(e)[:60])
            else:
                errors += 1
                logger.error("  ✗ {} failed: {}", stem, e)

    cursor.close()
    conn.close()

    logger.info("Done: imported={} skipped={} errors={}", imported, skipped, errors)


if __name__ == "__main__":
    import_all()
