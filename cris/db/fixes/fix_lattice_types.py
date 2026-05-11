"""
Баг 2: исправляет неверные типы решёток для Fe и W.

Причина бага: при ручном добавлении синтетических структур lattice_type_id
был взят неверно (попал monoclinic вместо cubic).

Что делает скрипт:
  1. Находит id для lattice_type WHERE name_en = 'cubic'
  2. Для каждой формулы из WRONG_LATTICE_FORMULAS — если текущий тип НЕ cubic,
     обновляет lattice_type_id → cubic_id
  3. Выводит что изменилось, а что уже было правильным

Запуск:
    python -m cris.db.fixes.fix_lattice_types
"""
import psycopg2
from cris.db.config import db_config
from cris.logger import logger

# Формулы, у которых гарантированно должна быть кубическая решётка (BCC/FCC/SC)
CUBIC_FORMULAS = {
    "Fe",   # α-железо — BCC, SG 229 (Im-3m)
    "W",    # вольфрам  — BCC, SG 229 (Im-3m)
    "Al",   # алюминий  — FCC, SG 225 (Fm-3m)
    "Cu",   # медь      — FCC, SG 225 (Fm-3m)
}


def fix_lattice_types(dry_run: bool = False) -> None:
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    try:
        # ── 1. Находим id кубической решётки ─────────────────────────────
        cur.execute("SELECT id FROM lattice_type WHERE name_en = 'cubic' LIMIT 1")
        row = cur.fetchone()
        if not row:
            logger.error("lattice_type 'cubic' not found in DB — run lattice_types_init first")
            return
        cubic_id = row[0]
        logger.info("cubic lattice_type id = {}", cubic_id)

        # ── 2. Смотрим что реально лежит в БД ───────────────────────────
        cur.execute("""
            SELECT rs.id, rs.formula, rs.name, rs.lattice_type_id, lt.name_en
            FROM reference_structure rs
            JOIN lattice_type lt ON lt.id = rs.lattice_type_id
            WHERE rs.formula = ANY(%s)
            ORDER BY rs.formula, rs.id
        """, (list(CUBIC_FORMULAS),))
        rows = cur.fetchall()

        if not rows:
            logger.info("No structures with formulas {} found in DB", CUBIC_FORMULAS)
            return

        fixed = []
        already_ok = []

        for struct_id, formula, name, lt_id, lt_name in rows:
            if lt_id == cubic_id:
                already_ok.append((struct_id, formula, name))
                logger.info("  OK — id={} '{}' ({}) already cubic", struct_id, name, formula)
            else:
                fixed.append((struct_id, formula, name, lt_name))
                logger.info(
                    "  FIX — id={} '{}' ({}) : {} → cubic",
                    struct_id, name, formula, lt_name
                )
                if not dry_run:
                    cur.execute(
                        "UPDATE reference_structure SET lattice_type_id = %s WHERE id = %s",
                        (cubic_id, struct_id)
                    )

        # ── 3. Итог ──────────────────────────────────────────────────────
        if dry_run:
            logger.info("[DRY RUN] Would fix {} record(s), {} already OK",
                        len(fixed), len(already_ok))
        else:
            conn.commit()
            logger.info("Done: fixed={}, already_ok={}", len(fixed), len(already_ok))

    except Exception as e:
        conn.rollback()
        logger.error("fix_lattice_types failed: {}", e)
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    import sys
    dry = "--dry-run" in sys.argv
    fix_lattice_types(dry_run=dry)
