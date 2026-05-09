"""
Основная логика поиска эталонных структур по нормализованным координатам.
Публичный интерфейс не изменился — main.py продолжает работать без правок.
"""
from collections import Counter
import mysql.connector
from cris.db.config import db_config


def get_similar_xyz_from_db(coordinates) -> list:
    """
    Ищет совпадения по нормализованным координатам в structure_site.
    coordinates: dict {n: [label, x, y, z]}
    Возвращает list строк: (site_id, lattice_type_id, structure_id, ...)
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    results = []
    try:
        query = """
            SELECT ss.id, rs.lattice_type_id, ss.structure_id
            FROM structure_site ss
            JOIN reference_structure rs ON rs.id = ss.structure_id
            WHERE ss.norm_x = %s AND ss.norm_y = %s AND ss.norm_z = %s
        """
        for _, x, y, z in list(coordinates.values()):
            cursor.execute(query, (x, y, z))
            results.extend(cursor.fetchall())
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        cursor.close()
        conn.close()
    return results


def check_coords(ions: list, ion_amount: int):
    """
    Фильтрует совпадения по количеству ионов.
    Возвращает [[lattice_names, substance_names], [top_lattice, prob], [top_substance, prob]]
    или False если ничего не найдено.
    """
    lattice_list   = [item[1] for item in ions]
    structure_list = [item[2] for item in ions]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    filtered_lattices   = []
    filtered_structures = []
    try:
        for i, struct_id in enumerate(structure_list):
            cursor.execute(
                "SELECT COUNT(*) FROM structure_site WHERE structure_id = %s",
                (struct_id,)
            )
            cnt = cursor.fetchone()[0]
            if cnt == ion_amount:
                filtered_lattices.append(lattice_list[i])
                filtered_structures.append(struct_id)
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        cursor.close()
        conn.close()

    if not filtered_lattices:
        return False

    lattice_counts = Counter(filtered_lattices)
    lattice_total  = sum(lattice_counts.values())
    lattice_probs  = {k: v / lattice_total * 100 for k, v in lattice_counts.items()}

    struct_counts  = Counter(filtered_structures)
    struct_total   = sum(struct_counts.values())
    struct_probs   = {k: v / struct_total * 100 for k, v in struct_counts.items()}

    top_lt_id   = max(lattice_probs, key=lattice_probs.get)
    top_lt_prob = lattice_probs[top_lt_id]
    top_st_id   = max(struct_probs,  key=struct_probs.get)
    top_st_prob = struct_probs[top_st_id]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    lattice_info   = None
    structure_info = None
    lattice_names  = []
    struct_names   = []
    try:
        for lt_id in set(filtered_lattices):
            cursor.execute(
                "SELECT id, name_en, name_ru, description FROM lattice_type WHERE id = %s",
                (lt_id,)
            )
            row = cursor.fetchone()
            if row:
                lattice_names.append([row[0], row[2], row[1], lattice_probs[lt_id]])
                if lt_id == top_lt_id:
                    lattice_info = row

        for st_id in set(filtered_structures):
            cursor.execute("""
                SELECT id, name, cell_length_a, cell_length_b, cell_length_c,
                       cell_volume, cell_angle_alpha, cell_angle_beta, cell_angle_gamma,
                       sg_number, sg_hall, sg_hm, doi
                FROM reference_structure WHERE id = %s
            """, (st_id,))
            row = cursor.fetchone()
            if row:
                struct_names.append([row[0], row[1], struct_probs[st_id]])
                if st_id == top_st_id:
                    structure_info = row
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        cursor.close()
        conn.close()

    return [
        [lattice_names, struct_names],
        [lattice_info, top_lt_prob],
        [structure_info, top_st_prob],
    ]
