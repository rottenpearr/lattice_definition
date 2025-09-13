import sys

import mysql.connector

from scripts.config import db_config
from scripts.coordinates_nondimensionalization import shift_coordinates, normalize_coordinates


def parse_xyz(xyz_file_path):
    with open(xyz_file_path, "r") as file:
        lines = file.readlines()

    atom_count = int(lines[0].strip())  # Первая строка содержит количество атомов
    data = []  # Список для хранения данных об атомах

    # Считываем данные об атомах (начиная с 3-й строки)
    for line in lines[2:2 + atom_count]:
        parts = line.split()
        atom_type = parts[0]  # Тип атома (например, Cl, Na)
        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])  # decimal
        data.append([atom_type, x, y, z])

    return data


def insert_data(cursor, data, normalized_data, lattice_type_id, substance_id):
    for i in range(len(data)):
        cursor.execute(
            """
            INSERT INTO ions_library (lattice_type_id, substance_id, atom_site_fract_x, atom_site_fract_y, atom_site_fract_z,
            atom_site_normalized_x, atom_site_normalized_y, atom_site_normalized_z)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (int(lattice_type_id), substance_id, data[i][1], data[i][2], data[i][3],
             normalized_data[i][1], normalized_data[i][2], normalized_data[i][3])
        )


if __name__ == '__main__':
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        xyz_file_path = sys.argv[1]
        data = parse_xyz(xyz_file_path)
        shifted_data = shift_coordinates(data)
        normalized_data = normalize_coordinates(shifted_data)
        lattice_type_id = sys.argv[2]
        substance_id = sys.argv[3]
        insert_data(cursor, data, normalized_data, lattice_type_id, substance_id)
        conn.commit()
        print("Данные из xyz успешно добавлены в базу данных.")
    except Exception as e:
        conn.rollback()
        print(f"Произошла ошибка: {e}")
    finally:
        cursor.close()
        conn.close()
