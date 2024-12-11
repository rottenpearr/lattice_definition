import json
import mysql.connector

from config import db_config

json_file_path = "data.json"


def insert_data(cursor, crystalline_system, lattice_system, description, ions, substances):
    cursor.execute(
        """
        INSERT INTO lattice_type (crystalline_system, lattice_system, description)
        VALUES (%s, %s, %s)
        """,
        (crystalline_system, lattice_system, description)
    )
    lattice_type_id = cursor.lastrowid  # Получаем ID вставленной строки

    # for ion in ions:
    #     cursor.execute(
    #         """
    #         INSERT INTO ions (lattice_type_id, x, y, z)
    #         VALUES (%s, %s, %s, %s)
    #         """,
    #         (lattice_type_id, ion["x"], ion["y"], ion["z"])
    #     )
    #     ion_id = cursor.lastrowid  # Получаем ID иона
    #
    #     cursor.execute(
    #         """
    #         INSERT INTO ion_library (ion_id, charge)
    #         VALUES (%s, %s)
    #         """,
    #         (ion_id, ion["charge"])
    #     )

    for substance in substances:
        cursor.execute(
            """
            INSERT INTO substances (name, lattice_type_id, similarity_coefficient)
            VALUES (%s, %s, %s)
            """,
            (substance["name"], lattice_type_id, substance["similarity_coefficient"])
        )

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

try:
    with open(json_file_path, "r") as file:
        data = json.load(file)
        print(#insert_data(
            cursor,
            data["data"]["values"]["_symmetry_cell_setting"][0],
            data["lattice_system"],
            data["description"],
            data["ions"],
            data["substances"]
        )
    conn.commit()
    print("Данные успешно добавлены в базу данных.")
except Exception as e:
    conn.rollback()
    print(f"Произошла ошибка: {e}")
finally:
    cursor.close()
    conn.close()
