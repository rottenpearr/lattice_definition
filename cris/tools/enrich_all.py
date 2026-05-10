"""
Массовое обогащение всех записей в БД из внешних источников.

Что делает:
  1. Все типы решёток (lattice_type) → обогащает через Claude AI → lattice_metadata
  2. Все вещества (reference_structure) → COD + Materials Project + robocrystallographer

Запуск:
    python -m cris.tools.enrich_all                # всё
    python -m cris.tools.enrich_all --lattices     # только типы решёток
    python -m cris.tools.enrich_all --structures   # только вещества
    python -m cris.tools.enrich_all --dry-run      # показать что будет, ничего не менять

Флаги пропуска (по умолчанию включены):
    --skip-enriched   пропускать записи, которые уже обогащались (по умолчанию: да)
    --force           обогащать заново даже если данные уже есть
"""
import argparse
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)

from cris.db.connection import get_cursor
from cris.db.enrichment.enricher import enrich_lattice_type, enrich_structure
from cris.logger import logger


# ─── загрузка данных из БД ────────────────────────────────────────────────────

def _load_lattice_types(skip_enriched: bool) -> list[tuple]:
    """Возвращает [(id, name_en, name_ru), ...] для обогащения."""
    with get_cursor() as cur:
        if skip_enriched:
            cur.execute("""
                SELECT lt.id, lt.name_en, lt.name_ru
                FROM lattice_type lt
                LEFT JOIN lattice_metadata lm ON lm.lattice_type_id = lt.id
                WHERE lm.lattice_type_id IS NULL
                ORDER BY lt.id
            """)
        else:
            cur.execute("SELECT id, name_en, name_ru FROM lattice_type ORDER BY id")
        return cur.fetchall()


def _load_structures(skip_enriched: bool) -> list[tuple]:
    """Возвращает [(id, formula, sg_number, cif_path, mp_id), ...] для обогащения."""
    with get_cursor() as cur:
        if skip_enriched:
            # пропускаем если оба внешних ID уже заполнены
            cur.execute("""
                SELECT id, formula, sg_number, cif_path, mp_id
                FROM reference_structure
                WHERE cod_id IS NULL OR mp_id IS NULL OR mp_id = ''
                ORDER BY id
            """)
        else:
            cur.execute("""
                SELECT id, formula, sg_number, cif_path, mp_id
                FROM reference_structure
                ORDER BY id
            """)
        return cur.fetchall()


# ─── обогащение решёток ───────────────────────────────────────────────────────

def run_lattice_enrichment(rows: list[tuple], dry_run: bool) -> None:
    total = len(rows)
    if total == 0:
        logger.info("Все типы решёток уже обогащены, пропускаем.")
        return

    logger.info("Обогащение типов решёток: {} записей", total)
    ok = fail = 0

    for i, (lt_id, name_en, name_ru) in enumerate(rows, 1):
        logger.info("[{}/{}] lattice_type id={} '{}'", i, total, lt_id, name_ru)
        if dry_run:
            continue
        success = enrich_lattice_type(lt_id)
        if success:
            ok += 1
        else:
            fail += 1
        # пауза чтобы не спамить API
        time.sleep(1.5)

    if not dry_run:
        logger.info("Решётки: {} успешно, {} ошибок", ok, fail)


# ─── обогащение структур ──────────────────────────────────────────────────────

def run_structure_enrichment(rows: list[tuple], dry_run: bool) -> None:
    total = len(rows)
    if total == 0:
        logger.info("Все структуры уже обогащены, пропускаем.")
        return

    logger.info("Обогащение структур: {} записей", total)
    ok = fail = 0

    for i, (st_id, formula, sg_number, cif_path, mp_id) in enumerate(rows, 1):
        formula_str = formula or "?"
        logger.info("[{}/{}] structure id={} formula='{}'", i, total, st_id, formula_str)
        if dry_run:
            continue

        # если mp_id уже есть — передаём чтобы robocrys не делал лишний запрос
        success = enrich_structure(
            structure_id=st_id,
            formula=formula_str,
            sg_number=sg_number or 0,
            cif_path=cif_path or "",
        )
        if success:
            ok += 1
        else:
            fail += 1
        # небольшая пауза между запросами к внешним API
        time.sleep(0.5)

    if not dry_run:
        logger.info("Структуры: {} успешно, {} ошибок", ok, fail)


# ─── точка входа ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Массовое обогащение БД из внешних источников")
    parser.add_argument("--lattices",    action="store_true", help="только типы решёток")
    parser.add_argument("--structures",  action="store_true", help="только вещества")
    parser.add_argument("--force",       action="store_true", help="не пропускать уже обогащённые")
    parser.add_argument("--dry-run",     action="store_true", help="показать план, ничего не менять")
    args = parser.parse_args()

    do_lattices  = args.lattices or (not args.lattices and not args.structures)
    do_structures = args.structures or (not args.lattices and not args.structures)
    skip_enriched = not args.force

    if args.dry_run:
        logger.info("=== DRY RUN — никаких изменений не будет ===")

    if do_lattices:
        rows = _load_lattice_types(skip_enriched)
        run_lattice_enrichment(rows, args.dry_run)

    if do_structures:
        rows = _load_structures(skip_enriched)
        run_structure_enrichment(rows, args.dry_run)

    logger.info("=== Готово ===")


if __name__ == "__main__":
    main()
