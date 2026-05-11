"""
Основная логика поиска эталонных структур по нормализованным координатам.
Публичный интерфейс не изменился — main.py продолжает работать без правок.
"""
from collections import Counter
from cris.db.connection import get_cursor
from cris.logger import logger


_COORD_TOLERANCE = 1e-4  # допуск при сравнении нормализованных координат


def get_similar_xyz_from_db(coordinates) -> list:
    """
    Ищет совпадения по нормализованным координатам в structure_site.
    coordinates: dict {n: [label, x, y, z]}
    Использует допуск ±_COORD_TOLERANCE вместо точного сравнения float.
    Возвращает list строк: (site_id, lattice_type_id, structure_id)
    """
    query = """
        SELECT ss.id, rs.lattice_type_id, ss.structure_id
        FROM structure_site ss
        JOIN reference_structure rs ON rs.id = ss.structure_id
        WHERE ss.norm_x BETWEEN %s AND %s
          AND ss.norm_y BETWEEN %s AND %s
          AND ss.norm_z BETWEEN %s AND %s
    """
    results = []
    try:
        with get_cursor() as cur:
            for _, x, y, z in list(coordinates.values()):
                cur.execute(query, (
                    x - _COORD_TOLERANCE, x + _COORD_TOLERANCE,
                    y - _COORD_TOLERANCE, y + _COORD_TOLERANCE,
                    z - _COORD_TOLERANCE, z + _COORD_TOLERANCE,
                ))
                results.extend(cur.fetchall())
    except Exception as e:
        logger.error("get_similar_xyz_from_db failed: {}", e)
    return results


def check_coords(ions: list, ion_amount: int):
    """
    Фильтрует совпадения по количеству ионов.
    Возвращает [[lattice_names, substance_names], [top_lattice, prob], [top_substance, prob]]
    или False если ничего не найдено.
    """
    lattice_list   = [item[1] for item in ions]
    structure_list = [item[2] for item in ions]

    filtered_lattices   = []
    filtered_structures = []
    try:
        with get_cursor() as cur:
            for i, struct_id in enumerate(structure_list):
                cur.execute(
                    "SELECT COUNT(*) FROM structure_site WHERE structure_id = %s",
                    (struct_id,)
                )
                cnt = cur.fetchone()[0]
                if cnt == ion_amount:
                    filtered_lattices.append(lattice_list[i])
                    filtered_structures.append(struct_id)
    except Exception as e:
        logger.error("check_coords (filter by count) failed: {}", e)

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

    lattice_names  = []
    struct_names   = []
    lattice_info   = None
    structure_info = None
    try:
        with get_cursor() as cur:
            for lt_id in set(filtered_lattices):
                cur.execute(
                    "SELECT id, name_en, name_ru, description FROM lattice_type WHERE id = %s",
                    (lt_id,)
                )
                row = cur.fetchone()
                if row:
                    lattice_names.append([row[0], row[2], row[1], lattice_probs[lt_id]])
                    if lt_id == top_lt_id:
                        lattice_info = row

            for st_id in set(filtered_structures):
                cur.execute("""
                    SELECT id, name, cell_length_a, cell_length_b, cell_length_c,
                           cell_volume, cell_angle_alpha, cell_angle_beta, cell_angle_gamma,
                           sg_number, sg_hall, sg_hm, doi, formula
                    FROM reference_structure WHERE id = %s
                """, (st_id,))
                row = cur.fetchone()
                if row:
                    struct_names.append([row[0], row[1], struct_probs[st_id]])
                    if st_id == top_st_id:
                        structure_info = row
    except Exception as e:
        logger.error("check_coords (fetch info) failed: {}", e)

    return [
        [lattice_names, struct_names],
        [lattice_info, top_lt_prob],
        [structure_info, top_st_prob],
    ]
