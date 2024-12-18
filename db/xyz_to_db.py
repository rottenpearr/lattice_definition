import mysql.connector
from pathlib import Path
from glob import glob

from config import db_config

xyz_files_path = Path("../data/xyz")
lattice_type_id_file_path = Path("lattice_type_id.txt")


def parse_txt(ion_ids_file_path):
    with open(ion_ids_file_path, "r") as file:
        id = file.readline()
    return int(id)


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


def insert_data(cursor, data, lattice_type_id):
    for atom_data in data:
        cursor.execute(
            """
            INSERT INTO ions_library (lattice_type_id, atom_site_fract_x, atom_site_fract_y, atom_site_fract_z)
            VALUES (%s, %s, %s, %s)
            """,
            (lattice_type_id, atom_data[1], atom_data[2], atom_data[3])
        )

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

try:
    lattice_type_id = parse_txt(lattice_type_id_file_path)
    xyz_files = glob(str(xyz_files_path / "*.xyz"))
    for xyz_file in xyz_files:
        data = parse_xyz(xyz_file)
        insert_data(cursor, data, lattice_type_id)
    conn.commit()
    print(f"Обработано файлов: {len(xyz_files)}.")
    print("Данные успешно добавлены в базу данных.")
except Exception as e:
    conn.rollback()
    print(f"Произошла ошибка: {e}")
finally:
    cursor.close()
    conn.close()
