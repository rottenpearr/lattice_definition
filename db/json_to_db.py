import json
import sys
from pathlib import Path

import mysql.connector

from config import db_config

json_files_path = Path("../data/json")

def insert_data(cursor, data):
    global lattice_type_id, substance_id

    try:
        _chemical_name_systematic = data["data"]["values"]["_chemical_name_systematic"][0]
    except Exception as _:
        _chemical_name_systematic = "No chemical name"
    _cell_length_a = float(data["data"]["values"]["_cell_length_a"][0].split("(")[0])
    _cell_length_b = float(data["data"]["values"]["_cell_length_b"][0].split("(")[0])
    _cell_length_c = float(data["data"]["values"]["_cell_length_c"][0].split("(")[0])
    _cell_volume = float(data["data"]["values"]["_cell_volume"][0].split("(")[0])
    _cell_angle_alpha = float(data["data"]["values"]["_cell_angle_alpha"][0].split("(")[0])
    _cell_angle_beta = float(data["data"]["values"]["_cell_angle_beta"][0].split("(")[0])
    _cell_angle_gamma = float(data["data"]["values"]["_cell_angle_gamma"][0].split("(")[0])
    _space_group_IT_number = data["data"]["values"]["_space_group_IT_number"][0]
    _symmetry_space_group_name_Hall = data["data"]["values"]["_symmetry_space_group_name_Hall"][0]
    _symmetry_space_group_name_H_M = data["data"]["values"]["_symmetry_space_group_name_H-M"][0]
    lattice_type_name = data["data"]["values"]["_symmetry_cell_setting"][0]
    cursor.execute(
        """
        SELECT id FROM lattice_type
        WHERE name_en = %s
        LIMIT 1
        """,
        (lattice_type_name,)
    )
    result = cursor.fetchone()
    if result:
        _lattice_type_id = result[0]
    else:
        _lattice_type_id = None  # такой результат выдаст ошибку

    lattice_type_id = _lattice_type_id

    cursor.execute(
        """
        INSERT INTO substances (name, cell_length_a, cell_length_b, cell_length_c, cell_volume, cell_angle_alpha, cell_angle_beta, cell_angle_gamma, space_group_IT_number, symmetry_space_group_name_Hall, symmetry_space_group_name_H_M, lattice_type_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (_chemical_name_systematic,
         _cell_length_a,
         _cell_length_b,
         _cell_length_c,
         _cell_volume,
         _cell_angle_alpha,
         _cell_angle_beta,
         _cell_angle_gamma,
         _space_group_IT_number,
         _symmetry_space_group_name_Hall,
         _symmetry_space_group_name_H_M,
         _lattice_type_id)
    )
    substance_id = cursor.lastrowid  # Получаем ID вставленной строки

    _atom_site_label_list = data["data"]["values"]["_atom_site_label"]
    _atom_site_type_symbol_list = data["data"]["values"]["_atom_site_type_symbol"]
    _atom_type_oxidation_number_list = data["data"]["values"]["_atom_type_oxidation_number"]
    _atom_site_symmetry_multiplicity_list = data["data"]["values"]["_atom_site_symmetry_multiplicity"]
    _atom_site_Wyckoff_symbol_list = data["data"]["values"]["_atom_site_Wyckoff_symbol"]
    _atom_site_occupancy_list = data["data"]["values"]["_atom_site_occupancy"]
    _atom_site_attached_hydrogens_list = data["data"]["values"]["_atom_site_attached_hydrogens"]
    _atom_site_calc_flag_list = data["data"]["values"]["_atom_site_calc_flag"]

    ion_amount = len(_atom_site_label_list)
    oxidation_id = 0
    oxidation_ion = _atom_site_type_symbol_list[0]
    for ion in range(ion_amount):
        if _atom_site_type_symbol_list[ion] != oxidation_ion:
            oxidation_id += 1
            oxidation_ion = _atom_site_type_symbol_list[ion]
        cursor.execute(
            """
            INSERT INTO ions (substance_id, atom_site_label, atom_site_type_symbol, atom_type_oxidation_number,atom_site_symmetry_multiplicity, atom_site_Wyckoff_symbol, atom_site_occupancy, atom_site_attached_hydrogens, atom_site_calc_flag)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (substance_id,
             _atom_site_label_list[ion],
             _atom_site_type_symbol_list[ion],
             float(_atom_type_oxidation_number_list[oxidation_id].split("(")[0]),
             int(_atom_site_symmetry_multiplicity_list[ion]),
             _atom_site_Wyckoff_symbol_list[ion],
             float(_atom_site_occupancy_list[ion].split("(")[0]),
             int(_atom_site_attached_hydrogens_list[ion]),
             _atom_site_calc_flag_list[ion])
        )


conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

try:
    json_file_path = sys.argv[1]
    lattice_type_id = None
    substance_id = None
    with open(json_file_path, "r") as file:
        data = json.load(file)
        insert_data(cursor, data)
    conn.commit()

    with open("json_additional_data.txt", "w") as file:
        file.write(str(lattice_type_id))
        file.write("\n")
        file.write(str(substance_id))

    print("Данные из json успешно добавлены в базу данных.")
except Exception as e:
    conn.rollback()
    print(f"Произошла ошибка: {e}")
finally:
    cursor.close()
    conn.close()
