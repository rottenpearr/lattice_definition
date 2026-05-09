"""
Загружает нормализованные XYZ-координаты в structure_site.
Обновляет записи, созданные json_to_db.py (они уже имеют site без координат),
или вставляет новые, если sites ещё не созданы.

Использование:
    python -m cris.db.importers.xyz_to_db <xyz_file> <lattice_type_id> <structure_id>
"""
import sys

import mysql.connector

from cris.db.config import db_config
from cris.core.coordinates import shift_coordinates, normalize_coordinates
from cris.logger import logger


def parse_xyz(xyz_file_path: str) -> list[list]:
    with open(xyz_file_path, "r") as f:
        lines = f.readlines()
    atom_count = int(lines[0].strip())
    data = []
    for line in lines[2:2 + atom_count]:
        parts = line.split()
        data.append([parts[0], float(parts[1]), float(parts[2]), float(parts[3])])
    return data


def upsert_sites(cursor, data: list, normalized: list,
                 structure_id: int, lattice_type_id: int) -> None:
    """
    Пытается UPDATE существующих sites по (structure_id, atom_symbol, порядковому номеру).
    Если sites ещё не созданы (json_to_db не запускался), делает INSERT.
    """
    cursor.execute(
        "SELECT id FROM structure_site WHERE structure_id = %s ORDER BY id",
        (structure_id,)
    )
    existing_ids = [row[0] for row in cursor.fetchall()]

    for i, (raw, norm) in enumerate(zip(data, normalized)):
        fract_x, fract_y, fract_z = raw[1], raw[2], raw[3]
        norm_x, norm_y, norm_z    = norm[1], norm[2], norm[3]

        if i < len(existing_ids):
            cursor.execute("""
                UPDATE structure_site
                SET fract_x = %s, fract_y = %s, fract_z = %s,
                    norm_x  = %s, norm_y  = %s, norm_z  = %s
                WHERE id = %s
            """, (fract_x, fract_y, fract_z, norm_x, norm_y, norm_z, existing_ids[i]))
        else:
            cursor.execute("""
                INSERT INTO structure_site
                    (structure_id, atom_symbol, fract_x, fract_y, fract_z,
                     norm_x, norm_y, norm_z)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (structure_id, raw[0],
                  fract_x, fract_y, fract_z,
                  norm_x, norm_y, norm_z))


if __name__ == "__main__":
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        xyz_path       = sys.argv[1]
        lattice_type_id = int(sys.argv[2])
        structure_id    = int(sys.argv[3])

        data       = parse_xyz(xyz_path)
        shifted    = shift_coordinates(data)
        normalized = normalize_coordinates(shifted)

        upsert_sites(cursor, data, normalized, structure_id, lattice_type_id)
        conn.commit()
        logger.info("Coordinates loaded: structure_id={}, {} sites", structure_id, len(data))
    except Exception as e:
        conn.rollback()
        logger.error("xyz_to_db failed: {}", e)
    finally:
        cursor.close()
        conn.close()
