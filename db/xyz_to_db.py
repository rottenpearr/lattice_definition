import mysql.connector
from config import db_config

def insert_data(cursor, crystalline_system, lattice_system, description, ions, substances):
    """
    Вставка данных в базу: lattice_type, ions, substances
    """
    # Вставка данных в lattice_type
    cursor.execute(
        """
        INSERT INTO lattice_type (crystalline_system, lattice_system, description)
        VALUES (%s, %s, %s)
        """,
        (crystalline_system, lattice_system, description)
    )
    lattice_type_id = cursor.lastrowid  # Получаем ID вставленной строки

    # Вставка данных об ионах
    for ion in ions:
        cursor.execute(
            """
            INSERT INTO ions (lattice_type_id, x, y, z)
            VALUES (%s, %s, %s, %s)
            """,
            (lattice_type_id, ion["x"], ion["y"], ion["z"])
        )

    # Вставка данных о веществах
    for substance in substances:
        cursor.execute(
            """
            INSERT INTO substances (name, lattice_type_id, similarity_coefficient)
            VALUES (%s, %s, %s)
            """,
            (substance["name"], lattice_type_id, substance["similarity_coefficient"])
        )

def parse_xyz(file_path):
    """
    Парсинг XYZ файла и подготовка данных для вставки
    """
    ions = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        num_atoms = int(lines[0].strip())  # Количество атомов
        description = lines[1].strip()     # Описание структуры

        # Чтение атомов и их координат
        for line in lines[2:2 + num_atoms]:
            parts = line.split()
            atom_type = parts[0]  # Тип атома (например, C, H, O)
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            ions.append({"atom_type": atom_type, "x": x, "y": y, "z": z})

    # Пример данных о веществах
    substances = [{"name": "Sample Substance", "similarity_coefficient": 0.85}]

    return description, ions, substances

# Подключение к базе данных
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

try:
    # Путь к XYZ файлу
    xyz_file = "example.xyz"

    # Парсинг XYZ файла
    crystalline_system = "Триклинная"  # Пример системы (можно изменить)
    lattice_system = "P"  # Пример решетки
    description, ions, substances = parse_xyz(xyz_file)

    # Вставка данных в базу
    insert_data(cursor, crystalline_system, lattice_system, description, ions, substances)

    # Подтверждение транзакции
    conn.commit()
    print("Данные успешно добавлены в базу данных.")

except Exception as e:
    conn.rollback()
    print(f"Произошла ошибка: {e}")

finally:
    cursor.close()
    conn.close()
