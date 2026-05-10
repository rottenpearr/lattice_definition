"""
Smoke-тест PostgreSQL: подключение, запись, чтение, очистка.
Запускать: python -m cris.tools.smoke_test_pg
"""
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)

from cris.db.connection import get_cursor
from cris.logger import logger


def run():
    # 1. Список таблиц
    with get_cursor() as cur:
        cur.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        tables = [r[0] for r in cur.fetchall()]
    logger.info("Tables in DB: {}", tables)
    assert len(tables) == 8, f"Expected 8 tables, got {len(tables)}: {tables}"

    # 2. Вставка тестового типа решётки
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO lattice_type (name_en, name_ru, crystal_system, bravais_lattice)
            VALUES ('cubic_test', 'кубическая_тест', 'cubic', 'F')
            RETURNING id
        """)
        lt_id = cur.fetchone()[0]
    logger.info("Inserted lattice_type id={}", lt_id)

    # 3. Вставка тестовой структуры
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO reference_structure (name, formula, lattice_type_id,
                cell_length_a, cell_length_b, cell_length_c,
                sg_number, existence_status)
            VALUES ('NaCl_test', 'NaCl', %s, 5.64, 5.64, 5.64, 225, 'experimental')
            RETURNING id
        """, (lt_id,))
        rs_id = cur.fetchone()[0]
    logger.info("Inserted reference_structure id={}", rs_id)

    # 4. Вставка позиции атома
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO structure_site
                (structure_id, atom_symbol, norm_x, norm_y, norm_z)
            VALUES (%s, 'Na', 0.0, 0.0, 0.0)
        """, (rs_id,))
    logger.info("Inserted structure_site for Na")

    # 5. Поиск по координатам
    with get_cursor() as cur:
        cur.execute("""
            SELECT ss.id, rs.name, lt.name_en
            FROM structure_site ss
            JOIN reference_structure rs ON rs.id = ss.structure_id
            JOIN lattice_type lt ON lt.id = rs.lattice_type_id
            WHERE ss.norm_x = 0.0 AND ss.norm_y = 0.0 AND ss.norm_z = 0.0
        """)
        rows = cur.fetchall()
    logger.info("Search result: {}", rows)
    assert len(rows) == 1
    assert rows[0][1] == "NaCl_test"
    assert rows[0][2] == "cubic_test"

    # 6. Очистка тестовых данных (CASCADE удалит структуру и сайт)
    with get_cursor() as cur:
        cur.execute("DELETE FROM lattice_type WHERE id = %s", (lt_id,))
    logger.info("Test data cleaned up")

    logger.info("=== Smoke test PASSED ===")


if __name__ == "__main__":
    run()
