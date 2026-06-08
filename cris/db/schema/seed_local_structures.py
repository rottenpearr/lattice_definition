"""
Заполняет reference_structure из локального манифеста (source_manifest.json).

Не требует MP_API_KEY — работает с XYZ-файлами, уже лежащими в репо.
Идемпотентен: INSERT ON CONFLICT (mp_id) DO UPDATE.

Запуск:
    python -m cris.db.schema.seed_local_structures
"""
import json
import sys
from pathlib import Path

import psycopg2
from cris.db.config import db_config

_ROOT         = Path(__file__).parent.parent.parent.parent
_MANIFEST     = _ROOT / "data" / "structures" / "micro" / "source_manifest.json"


def _get_or_create_lattice_type(cur, name_en: str | None) -> int | None:
    """Возвращает id типа решётки по name_en (регистр не важен)."""
    if not name_en:
        return None
    cur.execute(
        "SELECT id FROM lattice_type WHERE LOWER(name_en) = LOWER(%s) LIMIT 1",
        (name_en,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def seed_from_manifest(conn) -> tuple[int, int, int]:
    """
    Читает source_manifest.json и upsert-ит записи в reference_structure.
    Возвращает (inserted, updated, skipped).
    """
    if not _MANIFEST.exists():
        print(f"  WARN: манифест не найден: {_MANIFEST}")
        return 0, 0, 0

    with open(_MANIFEST, encoding="utf-8") as f:
        entries = json.load(f)

    cur = conn.cursor()
    inserted = updated = skipped = 0

    for entry in entries:
        mp_id    = entry.get("mp_id")
        xyz_rel  = entry.get("xyz_path", "")
        xyz_path = _ROOT / xyz_rel

        # Файл должен существовать на диске
        if not xyz_path.exists():
            print(f"  SKIP (file missing): {xyz_rel}")
            skipped += 1
            continue

        lt_id = _get_or_create_lattice_type(cur, entry.get("lattice_name_en"))

        try:
            # Upsert по mp_id
            cur.execute(
                "SELECT id FROM reference_structure WHERE mp_id = %s",
                (mp_id,)
            )
            existing = cur.fetchone()

            if existing:
                cur.execute("""
                    UPDATE reference_structure SET
                        name             = %s,
                        formula          = %s,
                        lattice_type_id  = COALESCE(%s, lattice_type_id),
                        cell_length_a    = %s,
                        cell_length_b    = %s,
                        cell_length_c    = %s,
                        cell_volume      = %s,
                        cell_angle_alpha = %s,
                        cell_angle_beta  = %s,
                        cell_angle_gamma = %s,
                        sg_number        = %s,
                        sg_hm            = %s,
                        xyz_path         = %s,
                        source_url       = %s
                    WHERE mp_id = %s
                """, (
                    entry.get("name") or entry.get("formula"),
                    entry.get("formula"),
                    lt_id,
                    entry.get("cell_length_a"),
                    entry.get("cell_length_b"),
                    entry.get("cell_length_c"),
                    entry.get("cell_volume"),
                    entry.get("cell_angle_alpha"),
                    entry.get("cell_angle_beta"),
                    entry.get("cell_angle_gamma"),
                    entry.get("sg_number"),
                    entry.get("sg_hm"),
                    xyz_rel,
                    entry.get("source_url"),
                    mp_id,
                ))
                updated += 1
            else:
                # Если lattice_type_id не определён — берём первый доступный
                if lt_id is None:
                    cur.execute("SELECT id FROM lattice_type ORDER BY id LIMIT 1")
                    row = cur.fetchone()
                    lt_id = row[0] if row else 1

                cur.execute("""
                    INSERT INTO reference_structure
                        (name, formula, lattice_type_id,
                         cell_length_a, cell_length_b, cell_length_c, cell_volume,
                         cell_angle_alpha, cell_angle_beta, cell_angle_gamma,
                         sg_number, sg_hm,
                         mp_id, xyz_path, source_url,
                         existence_status)
                    VALUES
                        (%s, %s, %s,
                         %s, %s, %s, %s,
                         %s, %s, %s,
                         %s, %s,
                         %s, %s, %s,
                         'experimental')
                """, (
                    entry.get("name") or entry.get("formula"),
                    entry.get("formula"),
                    lt_id,
                    entry.get("cell_length_a"),
                    entry.get("cell_length_b"),
                    entry.get("cell_length_c"),
                    entry.get("cell_volume"),
                    entry.get("cell_angle_alpha"),
                    entry.get("cell_angle_beta"),
                    entry.get("cell_angle_gamma"),
                    entry.get("sg_number"),
                    entry.get("sg_hm"),
                    mp_id,
                    xyz_rel,
                    entry.get("source_url"),
                ))
                inserted += 1

            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"  ERROR {mp_id}: {e}")
            skipped += 1

    cur.close()
    return inserted, updated, skipped


if __name__ == "__main__":
    print("Seeding reference_structure from local manifest...")
    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = False
        ins, upd, skip = seed_from_manifest(conn)
        conn.close()
        print(f"  Done: inserted={ins}, updated={upd}, skipped={skip}")
    except Exception as e:
        print(f"  FATAL: {e}")
        sys.exit(1)
