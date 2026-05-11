"""CRUD для reference_structure."""
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
