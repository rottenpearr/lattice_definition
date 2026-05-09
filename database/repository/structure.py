"""CRUD для эталонных структур (substances) и библиотеки ионов."""
from typing import Optional
from database.db import get_cursor
from database.models import ReferenceStructure


def get_structure(structure_id: int) -> Optional[ReferenceStructure]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, name, lattice_type_id, formula,
                   cell_length_a, cell_length_b, cell_length_c, cell_volume,
                   cell_angle_alpha, cell_angle_beta, cell_angle_gamma,
                   space_group_IT_number, symmetry_space_group_name_Hall, symmetry_space_group_name_H_M,
                   cif_path, xyz_path, image_path, cod_id, mp_id, icsd_id,
                   source_url, doi, added_at, updated_at
            FROM substances WHERE id = %s
        """, (structure_id,))
        row = cur.fetchone()
    return ReferenceStructure(*row) if row else None


def get_structures_by_lattice(lattice_type_id: int) -> list[ReferenceStructure]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, name, lattice_type_id, formula,
                   cell_length_a, cell_length_b, cell_length_c, cell_volume,
                   cell_angle_alpha, cell_angle_beta, cell_angle_gamma,
                   space_group_IT_number, symmetry_space_group_name_Hall, symmetry_space_group_name_H_M,
                   cif_path, xyz_path, image_path, cod_id, mp_id, icsd_id,
                   source_url, doi, added_at, updated_at
            FROM substances WHERE lattice_type_id = %s
        """, (lattice_type_id,))
        rows = cur.fetchall()
    return [ReferenceStructure(*row) for row in rows]


def update_structure_paths(structure_id: int, *, cif_path: str = "", xyz_path: str = "",
                           image_path: str = "") -> None:
    with get_cursor() as cur:
        cur.execute("""
            UPDATE substances
            SET cif_path   = COALESCE(NULLIF(%s, ''), cif_path),
                xyz_path   = COALESCE(NULLIF(%s, ''), xyz_path),
                image_path = COALESCE(NULLIF(%s, ''), image_path)
            WHERE id = %s
        """, (cif_path, xyz_path, image_path, structure_id))


def update_structure_external_ids(structure_id: int, *,
                                  cod_id: Optional[int] = None,
                                  mp_id: str = "",
                                  doi: str = "",
                                  source_url: str = "") -> None:
    with get_cursor() as cur:
        cur.execute("""
            UPDATE substances
            SET cod_id     = COALESCE(%s, cod_id),
                mp_id      = COALESCE(NULLIF(%s, ''), mp_id),
                doi        = COALESCE(NULLIF(%s, ''), doi),
                source_url = COALESCE(NULLIF(%s, ''), source_url)
            WHERE id = %s
        """, (cod_id, mp_id, doi, source_url, structure_id))


def find_matching_structures(normalized_coords: list[tuple[float, float, float]],
                             ion_count: int) -> list[tuple]:
    """
    Повторяет логику ions_query.py, но через новый db-слой.
    Возвращает raw-строки из ions_library + substances для дальнейшей обработки.
    """
    with get_cursor() as cur:
        placeholders = []
        params = []
        for x, y, z in normalized_coords:
            placeholders.append("(atom_site_normalized_x = %s AND atom_site_normalized_y = %s "
                                "AND atom_site_normalized_z = %s)")
            params.extend([x, y, z])

        where_clause = " OR ".join(placeholders)
        cur.execute(f"""
            SELECT il.lattice_type_id, il.substance_id,
                   s.name, lt.name_ru, lt.name_en,
                   s.cell_length_a, s.cell_length_b, s.cell_length_c,
                   s.cell_volume, s.cell_angle_alpha, s.cell_angle_beta, s.cell_angle_gamma,
                   s.space_group_IT_number, s.symmetry_space_group_name_Hall,
                   s.symmetry_space_group_name_H_M, lt.description, s.doi
            FROM ions_library il
            JOIN substances s  ON s.id  = il.substance_id
            JOIN lattice_type lt ON lt.id = il.lattice_type_id
            WHERE {where_clause}
        """, params)
        hits = cur.fetchall()

    # Фильтрация: только вещества, у которых ровно ion_count ионов
    substance_ids = {row[1] for row in hits}
    if not substance_ids:
        return []

    with get_cursor() as cur:
        fmt = ",".join(["%s"] * len(substance_ids))
        cur.execute(f"SELECT substance_id, COUNT(*) FROM ions_library "
                    f"WHERE substance_id IN ({fmt}) GROUP BY substance_id", list(substance_ids))
        counts = {sid: cnt for sid, cnt in cur.fetchall()}

    return [row for row in hits if counts.get(row[1], 0) == ion_count]
