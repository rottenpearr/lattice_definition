"""
Импортирует метаданные структуры из JSON (конвертированного из CIF) в reference_structure.
Также заполняет structure_site полями из CIF (без координат — координаты грузит xyz_to_db.py).

Использование:
    python -m cris.db.importers.json_to_db data/db/json/NaCl.json
"""
import json
import sys
from pathlib import Path

import mysql.connector

from cris.db.config import db_config
from cris.logger import logger


def _float(s: str) -> float:
    return float(str(s).split("(")[0])


def insert_data(cursor, data: dict) -> tuple[int, int]:
    """Возвращает (lattice_type_id, structure_id)."""
    vals = data["data"]["values"]

    try:
        name = vals["_chemical_name_systematic"][0]
    except (KeyError, IndexError):
        name = "Unknown"

    a     = _float(vals["_cell_length_a"][0])
    b     = _float(vals["_cell_length_b"][0])
    c     = _float(vals["_cell_length_c"][0])
    vol   = _float(vals["_cell_volume"][0])
    alpha = _float(vals["_cell_angle_alpha"][0])
    beta  = _float(vals["_cell_angle_beta"][0])
    gamma = _float(vals["_cell_angle_gamma"][0])
    sg_num  = vals["_space_group_IT_number"][0]
    sg_hall = vals["_symmetry_space_group_name_Hall"][0]
    sg_hm   = vals["_symmetry_space_group_name_H-M"][0]
    lattice_type_name = vals["_symmetry_cell_setting"][0]

    cursor.execute("SELECT id FROM lattice_type WHERE name_en = %s LIMIT 1", (lattice_type_name,))
    row = cursor.fetchone()
    lattice_type_id = row[0] if row else None

    cursor.execute("""
        INSERT INTO reference_structure
            (name, lattice_type_id,
             cell_length_a, cell_length_b, cell_length_c, cell_volume,
             cell_angle_alpha, cell_angle_beta, cell_angle_gamma,
             sg_number, sg_hall, sg_hm)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, lattice_type_id, a, b, c, vol, alpha, beta, gamma,
          sg_num, sg_hall, sg_hm))
    structure_id = cursor.lastrowid

    labels      = vals.get("_atom_site_label", [])
    symbols     = vals.get("_atom_site_type_symbol", [])
    oxidations  = vals.get("_atom_type_oxidation_number", [])
    multipls    = vals.get("_atom_site_symmetry_multiplicity", [])
    wyckoffs    = vals.get("_atom_site_Wyckoff_symbol", [])
    occupancies = vals.get("_atom_site_occupancy", [])

    oxidation_idx = 0
    prev_symbol = symbols[0] if symbols else None
    for i, label in enumerate(labels):
        sym = symbols[i] if i < len(symbols) else ""
        if sym != prev_symbol:
            oxidation_idx += 1
            prev_symbol = sym
        oxi = _float(oxidations[oxidation_idx]) if oxidation_idx < len(oxidations) else None
        cursor.execute("""
            INSERT INTO structure_site
                (structure_id, atom_label, atom_symbol, oxidation,
                 multiplicity, wyckoff, occupancy)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            structure_id, label, sym, oxi,
            int(multipls[i]) if i < len(multipls) else None,
            wyckoffs[i] if i < len(wyckoffs) else None,
            _float(occupancies[i]) if i < len(occupancies) else 1.0,
        ))

    return lattice_type_id, structure_id


if __name__ == "__main__":
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        json_file_path = sys.argv[1]
        with open(json_file_path, "r") as f:
            data = json.load(f)
        lt_id, struct_id = insert_data(cursor, data)
        conn.commit()

        out_file = Path(__file__).parent / "json_additional_data.txt"
        out_file.write_text(f"{lt_id}\n{struct_id}")
        logger.info("Structure imported: lattice_type_id={}, structure_id={}", lt_id, struct_id)
    except Exception as e:
        conn.rollback()
        logger.error("json_to_db failed: {}", e)
    finally:
        cursor.close()
        conn.close()
