"""CRUD для reference_structure и structure_site."""
from typing import Optional
from cris.db.connection import get_cursor
from cris.db.models import ReferenceStructure


_SELECT = """
    SELECT id, name, formula, lattice_type_id,
           cell_length_a, cell_length_b, cell_length_c, cell_volume,
           cell_angle_alpha, cell_angle_beta, cell_angle_gamma,
           sg_number, sg_hall, sg_hm,
           cif_path, xyz_path, image_path,
           cod_id, mp_id, icsd_id, doi, source_url,
           existence_status, existence_source,
           structure_description
    FROM reference_structure
"""


def get_by_id(structure_id: int) -> Optional[ReferenceStructure]:
    with get_cursor() as cur:
        cur.execute(_SELECT + "WHERE id = %s", (structure_id,))
        row = cur.fetchone()
    return ReferenceStructure(*row) if row else None


def get_by_lattice_type(lattice_type_id: int) -> list[ReferenceStructure]:
    with get_cursor() as cur:
        cur.execute(_SELECT + "WHERE lattice_type_id = %s", (lattice_type_id,))
        return [ReferenceStructure(*row) for row in cur.fetchall()]


def update_file_paths(structure_id: int, *, cif_path: str = "",
                      xyz_path: str = "", image_path: str = "") -> None:
    with get_cursor() as cur:
        cur.execute("""
            UPDATE reference_structure
            SET cif_path   = COALESCE(NULLIF(%s,''), cif_path),
                xyz_path   = COALESCE(NULLIF(%s,''), xyz_path),
                image_path = COALESCE(NULLIF(%s,''), image_path)
            WHERE id = %s
        """, (cif_path, xyz_path, image_path, structure_id))


def update_external_ids(structure_id: int, *, cod_id: Optional[int] = None,
                        mp_id: str = "", doi: str = "", source_url: str = "") -> None:
    with get_cursor() as cur:
        cur.execute("""
            UPDATE reference_structure
            SET cod_id     = COALESCE(%s, cod_id),
                mp_id      = COALESCE(NULLIF(%s,''), mp_id),
                doi        = COALESCE(NULLIF(%s,''), doi),
                source_url = COALESCE(NULLIF(%s,''), source_url)
            WHERE id = %s
        """, (cod_id, mp_id, doi, source_url, structure_id))


def find_matching(normalized_coords: list[tuple[float, float, float]],
                  ion_count: int) -> list[tuple]:
    """
    Ищет эталоны с совпадающими нормализованными координатами
    и строго нужным количеством ионов.
    Возвращает строки (lattice_type_id, structure_id, name, name_ru, ...).
    """
    if not normalized_coords:
        return []

    placeholders = " OR ".join(
        ["(ss.norm_x=%s AND ss.norm_y=%s AND ss.norm_z=%s)"] * len(normalized_coords)
    )
    params = [v for xyz in normalized_coords for v in xyz]

    with get_cursor() as cur:
        cur.execute(f"""
            SELECT rs.lattice_type_id, ss.structure_id,
                   rs.name, lt.name_ru, lt.name_en, lt.description,
                   rs.cell_length_a, rs.cell_length_b, rs.cell_length_c,
                   rs.cell_volume, rs.cell_angle_alpha, rs.cell_angle_beta, rs.cell_angle_gamma,
                   rs.sg_number, rs.sg_hall, rs.sg_hm, rs.doi
            FROM structure_site ss
            JOIN reference_structure rs ON rs.id = ss.structure_id
            JOIN lattice_type lt         ON lt.id = rs.lattice_type_id
            WHERE {placeholders}
        """, params)
        hits = cur.fetchall()

    if not hits:
        return []

    struct_ids = {row[1] for row in hits}
    fmt = ",".join(["%s"] * len(struct_ids))
    with get_cursor() as cur:
        cur.execute(
            f"SELECT structure_id, COUNT(*) FROM structure_site "
            f"WHERE structure_id IN ({fmt}) GROUP BY structure_id",
            list(struct_ids)
        )
        counts = {sid: cnt for sid, cnt in cur.fetchall()}

    return [row for row in hits if counts.get(row[1], 0) == ion_count]
