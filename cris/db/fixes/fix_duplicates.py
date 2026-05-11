"""
Баг 1: удаляет дублирующиеся синтетические структуры.

Ситуация:
  - NaCl:  id=3  (synthetic, formula="NaCl",  без xyz_path)
           id=22 (COD,       formula="Cl Na", с xyz_path, cod_id=1000041)
  - MgO:   id=19 (synthetic, formula="MgO",   без xyz_path)
           id=25 (COD,       formula="Mg O",  с xyz_path, cod_id=1000053)

Стратегия:
  1. Перевешиваем recognition_result.predicted_structure_id: loser → winner
  2. Перевешиваем substance_info: если у winner уже есть — просто дадим CASCADE удалить
     лузерскую; если нет — UPDATE structure_id с loser на winner
  3. Удаляем reference_structure loser (CASCADE убирает substance_info)

ВАЖНО: recognition_result имеет ON DELETE SET NULL, поэтому перевешиваем ДО удаления.

Запуск:
    python -m cris.db.fixes.fix_duplicates            # реальное исполнение
    python -m cris.db.fixes.fix_duplicates --dry-run  # только показать план
"""
import sys
import psycopg2
from cris.db.config import db_config
from cris.logger import logger

# (loser_id, winner_id)
# loser  — синтетическая запись без координат (удаляем)
# winner — COD-запись с реальными координатами (оставляем)
PAIRS = [
    (3,  22),   # NaCl synthetic → NaCl COD (Cl Na, cod_id=1000041)
    (19, 25),   # MgO  synthetic → MgO  COD (Mg O,  cod_id=1000053)
]


def _describe(cur, struct_id: int) -> str:
    cur.execute("""
        SELECT rs.formula, rs.name, rs.cod_id,
               (rs.xyz_path IS NOT NULL AND rs.xyz_path != '') AS has_xyz
        FROM reference_structure rs WHERE rs.id = %s
    """, (struct_id,))
    row = cur.fetchone()
    if not row:
        return f"id={struct_id} [NOT FOUND]"
    formula, name, cod_id, has_xyz = row
    return (f"id={struct_id} formula='{formula}' name='{name}' "
            f"cod_id={cod_id} has_xyz={has_xyz}")


def fix_duplicates(dry_run: bool = False) -> None:
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    try:
        for loser_id, winner_id in PAIRS:
            loser_desc  = _describe(cur, loser_id)
            winner_desc = _describe(cur, winner_id)

            # Проверяем что оба существуют
            cur.execute("SELECT id FROM reference_structure WHERE id = %s", (loser_id,))
            if not cur.fetchone():
                logger.info("SKIP pair ({}, {}): loser id={} already gone",
                            loser_id, winner_id, loser_id)
                continue

            cur.execute("SELECT id FROM reference_structure WHERE id = %s", (winner_id,))
            if not cur.fetchone():
                logger.warning("SKIP pair ({}, {}): winner id={} not found — check PAIRS",
                               loser_id, winner_id, winner_id)
                continue

            logger.info("DUPLICATE pair:")
            logger.info("  KEEP   {}", winner_desc)
            logger.info("  DELETE {}", loser_desc)

            if dry_run:
                continue

            # -- a. Перевешиваем recognition_result --------------------------
            cur.execute("""
                UPDATE recognition_result
                SET predicted_structure_id = %s
                WHERE predicted_structure_id = %s
            """, (winner_id, loser_id))
            if cur.rowcount:
                logger.info("  Moved {} recognition_result rows -> winner", cur.rowcount)

            # -- b. Перевешиваем substance_info ------------------------------
            cur.execute("SELECT id FROM substance_info WHERE structure_id = %s", (winner_id,))
            winner_has_si = cur.fetchone() is not None

            cur.execute("SELECT id FROM substance_info WHERE structure_id = %s", (loser_id,))
            loser_has_si = cur.fetchone() is not None

            if loser_has_si and not winner_has_si:
                cur.execute("""
                    UPDATE substance_info SET structure_id = %s WHERE structure_id = %s
                """, (winner_id, loser_id))
                logger.info("  Moved substance_info from loser -> winner")
            elif loser_has_si and winner_has_si:
                logger.info("  Both have substance_info — loser's will be cascade-deleted")

            # -- c. Удаляем loser (CASCADE: substance_info) ------------------
            cur.execute("DELETE FROM reference_structure WHERE id = %s", (loser_id,))
            logger.info("  Deleted reference_structure id={}", loser_id)

        if not dry_run:
            conn.commit()
            logger.info("fix_duplicates: done")
        else:
            logger.info("[DRY RUN] No changes made")

    except Exception as e:
        conn.rollback()
        logger.error("fix_duplicates failed: {}", e)
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    fix_duplicates(dry_run=dry)
