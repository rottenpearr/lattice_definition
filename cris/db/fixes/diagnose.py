"""
Диагностика БД — показывает все известные проблемы без изменений.

Запуск:
    python -m cris.db.fixes.diagnose

Выводит:
  1. Все типы решёток с id
  2. Все reference_structure: id, formula, name, lattice_type, кол-во sites
  3. Дублирующиеся формулы
  4. Структуры без координат
  5. substance_info: что заполнено, что нет
"""
import sys
import psycopg2
from cris.db.config import db_config

# Принудительно UTF-8 в Windows-терминале
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OK   = "[OK]"
WARN = "[!!]"
MISS = "[--]"


def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def diagnose() -> None:
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # -- 1. Типы решёток -------------------------------------------------------
    _section("1. Типы решёток (lattice_type)")
    cur.execute("SELECT id, name_en, name_ru FROM lattice_type ORDER BY id")
    for row in cur.fetchall():
        print(f"  id={row[0]:3d}  {row[1]:<20s}  ({row[2]})")

    # -- 2. Все структуры ------------------------------------------------------
    _section("2. Все структуры (reference_structure)")
    cur.execute("""
        SELECT rs.id, rs.formula, rs.name, lt.name_en,
               rs.cod_id, rs.mp_id,
               (rs.xyz_path IS NOT NULL AND rs.xyz_path != '') AS has_xyz,
               (SELECT COUNT(*) FROM substance_info si WHERE si.structure_id = rs.id) AS has_si
        FROM reference_structure rs
        JOIN lattice_type lt ON lt.id = rs.lattice_type_id
        ORDER BY rs.id
    """)
    rows = cur.fetchall()
    print(f"  {'id':>4}  {'formula':<12}  {'lattice':<16}  {'cod_id':<10}  "
          f"{'mp_id':<14}  {'xyz':>4}  {'subinf':>6}  name")
    print(f"  {'-'*4}  {'-'*12}  {'-'*16}  {'-'*10}  {'-'*14}  {'-'*4}  {'-'*6}  {'-'*30}")
    for struct_id, formula, name, lt_name, cod_id, mp_id, has_xyz, has_si in rows:
        si_mark  = OK   if has_si  else MISS
        xyz_mark = OK   if has_xyz else WARN
        cod_str  = str(cod_id) if cod_id else "---"
        mp_str   = str(mp_id)  if mp_id  else "---"
        print(f"  {struct_id:>4}  {(formula or ''):12s}  {lt_name:<16s}  {cod_str:<10s}  "
              f"{mp_str:<14s}  {xyz_mark:>4}  {si_mark:>6}  {name or ''}")

    # -- 3. Дубликаты ----------------------------------------------------------
    _section("3. Дублирующиеся формулы")
    cur.execute("""
        SELECT REPLACE(formula, ' ', '') AS f_norm, COUNT(*) AS cnt,
               STRING_AGG(id::text, ', ' ORDER BY id) AS ids
        FROM reference_structure
        WHERE formula IS NOT NULL
        GROUP BY REPLACE(formula, ' ', '')
        HAVING COUNT(*) > 1
    """)
    dups = cur.fetchall()
    if dups:
        for f_norm, cnt, ids in dups:
            print(f"  {WARN} formula~'{f_norm}': {cnt} записи, ids = [{ids}]")
    else:
        print(f"  {OK} Дубликатов нет")

    # -- 4. Структуры без XYZ-файла -------------------------------------------
    _section("4. Структуры БЕЗ xyz_path")
    cur.execute("""
        SELECT rs.id, rs.formula, rs.name, lt.name_en
        FROM reference_structure rs
        JOIN lattice_type lt ON lt.id = rs.lattice_type_id
        WHERE rs.xyz_path IS NULL OR rs.xyz_path = ''
        ORDER BY rs.id
    """)
    no_xyz = cur.fetchall()
    if no_xyz:
        for struct_id, formula, name, lt_name in no_xyz:
            print(f"  {WARN} id={struct_id:>3d}  {(formula or ''):12s}  {lt_name:<16s}  {name or ''}")
        print(f"\n  Итого без xyz_path: {len(no_xyz)}")
    else:
        print(f"  {OK} Все структуры имеют xyz_path")

    # -- 5. Потенциально неверные типы решёток --------------------------------
    _section("5. Потенциальные ошибки типа решётки")
    cur.execute("""
        SELECT rs.id, rs.formula, rs.name, lt.name_en
        FROM reference_structure rs
        JOIN lattice_type lt ON lt.id = rs.lattice_type_id
        WHERE rs.formula IN ('Fe', 'W', 'Al', 'Cu')
          AND lt.name_en != 'cubic'
    """)
    wrong = cur.fetchall()
    if wrong:
        for struct_id, formula, name, lt_name in wrong:
            print(f"  {WARN} id={struct_id}  {formula}  '{name}'  -> {lt_name}  (ожидается cubic)")
    else:
        print(f"  {OK} Явных ошибок не обнаружено")

    # -- 6. substance_info ----------------------------------------------------
    _section("6. substance_info: полнота данных")
    cur.execute("""
        SELECT si.structure_id, rs.formula, rs.name,
               (si.description IS NOT NULL AND si.description != '') AS has_desc,
               (si.applications IS NOT NULL AND si.applications != '') AS has_app,
               (si.hazards IS NOT NULL AND si.hazards != '') AS has_haz,
               si.properties IS NOT NULL AS has_props,
               si.scientific_sources IS NOT NULL AS has_sources,
               si.enrichment_source
        FROM substance_info si
        JOIN reference_structure rs ON rs.id = si.structure_id
        ORDER BY si.structure_id
    """)
    si_rows = cur.fetchall()
    if si_rows:
        print(f"  {'id':>4}  {'formula':<12}  {'desc':>4}  {'app':>3}  {'haz':>3}  "
              f"{'props':>5}  {'srcs':>4}  source")
        for sid, formula, name, d, a, h, p, s, src in si_rows:
            def mark(v): return OK if v else MISS
            print(f"  {sid:>4}  {(formula or ''):12s}  "
                  f"{mark(d):>4}  {mark(a):>3}  {mark(h):>3}  "
                  f"{mark(p):>5}  {mark(s):>4}  {src or '---'}")
    else:
        print("  substance_info пуст")

    cur.execute("""
        SELECT COUNT(*) FROM reference_structure rs
        WHERE NOT EXISTS (SELECT 1 FROM substance_info si WHERE si.structure_id = rs.id)
    """)
    missing_si = cur.fetchone()[0]
    if missing_si:
        print(f"\n  {WARN} {missing_si} структур без substance_info")

    cur.close()
    conn.close()
    print("\n" + "=" * 60)


if __name__ == "__main__":
    diagnose()
