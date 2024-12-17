import mysql.connector
from pathlib import Path

from config import db_config

xyz_file_path = Path("../data/xyz/1000041.xyz")  # TODO: sys.args
ion_ids_file_path = Path("ion_ids.txt")


def parse_txt(ion_ids_file_path):
    with open(ion_ids_file_path, "r") as file:
        lines = file.readlines()
    return list(int(item) for item in lines)


def parse_xyz(xyz_file_path):
    with open(xyz_file_path, "r") as file:
        lines = file.readlines()

    atom_count = int(lines[0].strip())  # Первая строка содержит количество атомов
    data = []  # Список для хранения данных об атомах

    # Считываем данные об атомах (начиная с 3-й строки)
    for line in lines[2:2 + atom_count]:
        parts = line.split()
        atom_type = parts[0]  # Тип атома (например, Cl, Na)
        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
        data.append([atom_type, x, y, z])

    return data


def insert_data(cursor, data, ion_ids):
    id = 0
    if not data:
        return
    current_atom_type = data[0][0]
    for atom_data in data:
        if current_atom_type != atom_data[0]:
            current_atom_type = atom_data[0]
            id += 1
        ion_library_id = ion_ids[id]
        cursor.execute(
            """
            INSERT INTO ions (ion_library_id, atom_site_fract_x, atom_site_fract_y, atom_site_fract_z)
            VALUES (%s, %s, %s, %s)
            """,
            (ion_library_id, atom_data[1], atom_data[2], atom_data[3])
        )

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

try:
    ion_ids = parse_txt(ion_ids_file_path)
    data = parse_xyz(xyz_file_path)
    insert_data(cursor, data, ion_ids)
    conn.commit()
    print("Данные успешно добавлены в базу данных.")
except Exception as e:
    conn.rollback()
    print(f"Произошла ошибка: {e}")
finally:
    cursor.close()
    conn.close()
