from collections import Counter

import mysql.connector

from scripts.config import db_config


def get_similar_xyz_from_db(coordinates):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    results = []
    try:
        query = """
            SELECT * FROM ions_library
            WHERE atom_site_normalized_x = %s AND atom_site_normalized_y = %s AND atom_site_normalized_z = %s
        """
        for _, x, y, z in list(coordinates.values()):
            cursor.execute(query, (x, y, z))
            res = cursor.fetchall()
            for row in res:
                results.append(row)
    except Exception as e:
        conn.rollback()
        print(f"Произошла ошибка: {e}")
    finally:
        cursor.close()
        conn.close()
    return results


def check_coords(ions, ion_amount):
    lattice_list = [item[1] for item in ions]
    substance_list = [item[2] for item in ions]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    new_lattice_list = []
    new_substance_list = []
    try:
        query = """
            SELECT * FROM ions_library
            WHERE substance_id = %s
        """
        i = 0
        for id in substance_list:
            cursor.execute(query, [id])
            rows_amount = len(cursor.fetchall())
            if rows_amount == ion_amount:  # Проверяем, что кол-во ионов строго совпадает с введенным
                new_lattice_list.append(lattice_list[i])
                new_substance_list.append(substance_list[i])
            i += 1
    except Exception as e:
        conn.rollback()
        print(f"Произошла ошибка: {e}")
    finally:
        cursor.close()
        conn.close()
    lattice_list = new_lattice_list
    substance_list = new_substance_list

    lattice_counts = Counter(lattice_list)
    lattice_total = sum(lattice_counts.values())
    lattice_probabilities = {name: (count / lattice_total) * 100 for name, count in lattice_counts.items()}
    sorted_lattice_probabilities = sorted(lattice_probabilities.items(), key=lambda x: x[1], reverse=True)

    substance_counts = Counter(substance_list)
    substance_total = sum(substance_counts.values())
    substance_probabilities = {name: (count / substance_total) * 100 for name, count in substance_counts.items()}
    sorted_substance_probabilities = sorted(substance_probabilities.items(), key=lambda x: x[1], reverse=True)

    if not sorted_lattice_probabilities:
        return False

    lattice_names = []
    substance_names = []

    lattice_info_list = []
    lattice_info = None
    top_lattice_id = sorted_lattice_probabilities[0][0]
    top_lattice_probability = sorted_lattice_probabilities[0][1]

    substance_info_list = []
    substance_info = None
    top_substance_id = sorted_substance_probabilities[0][0]
    top_substance_probability = sorted_substance_probabilities[0][1]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        query = """
            SELECT * FROM lattice_type
            WHERE id = %s
        """
        for id in lattice_list:
            cursor.execute(query, [id])
            lattice_info_list.append(cursor.fetchall())

        query = """
            SELECT * FROM substances
            WHERE id = %s
        """
        for id in substance_list:
            cursor.execute(query, [id])
            substance_info_list.append(cursor.fetchall())

        for lattice in lattice_info_list:
            lattice = lattice[0]
            if not ([lattice[0], lattice[2], lattice[1]] in lattice_names):
                lattice_names.append([lattice[0], lattice[2], lattice[1]])
            if lattice[0] == top_lattice_id:
                lattice_info = lattice

        for substance in substance_info_list:
            substance = substance[0]
            if not([substance[0], substance[1]] in substance_names):
                substance_names.append([substance[0], substance[1]])
            if substance[0] == top_substance_id:
                substance_info = substance

        for i in range(len(lattice_names)):
            id = lattice_names[i][0]
            probability = lattice_probabilities[id]
            lattice_names[i].append(probability)

        for i in range(len(substance_names)):
            id = substance_names[i][0]
            probability = substance_probabilities[id]
            substance_names[i].append(probability)

    except Exception as e:
        conn.rollback()
        print(f"Произошла ошибка: {e}")
    finally:
        cursor.close()
        conn.close()

    return [[lattice_names, substance_names], [lattice_info, top_lattice_probability], [substance_info, top_substance_probability]]
