import mysql.connector
from pathlib import Path

from config import db_config

def test():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # try:
    #     ion_ids = parse_txt(ion_ids_file_path)
    #     data = parse_xyz(xyz_file_path)
    #     insert_data(cursor, data, ion_ids)
    #     conn.commit()
    #     print("Данные успешно добавлены в базу данных.")
    # except Exception as e:
    #     conn.rollback()
    #     print(f"Произошла ошибка: {e}")
    # finally:
    #     cursor.close()
    #     conn.close()