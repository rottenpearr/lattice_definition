"""CRUD для lattice_type и lattice_metadata."""
from datetime import datetime
from typing import Optional
from cris.db.connection import get_cursor
from cris.db.models import LatticeType, LatticeMetadata


def get_all() -> list[LatticeType]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, name_en, name_ru, crystal_system, bravais_lattice,
                   point_group, sg_number_min, sg_number_max, description
            FROM lattice_type
        """)
        return [LatticeType(*row) for row in cur.fetchall()]


def get_by_id(lattice_type_id: int) -> Optional[LatticeType]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, name_en, name_ru, crystal_system, bravais_lattice,
                   point_group, sg_number_min, sg_number_max, description
            FROM lattice_type WHERE id = %s
        """, (lattice_type_id,))
        row = cur.fetchone()
    return LatticeType(*row) if row else None


def get_metadata(lattice_type_id: int) -> Optional[LatticeMetadata]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT lattice_type_id, discoverer, discovery_year, discovery_context,
                   wiki_url, review_doi, notes, enriched_at, enrichment_source
            FROM lattice_metadata WHERE lattice_type_id = %s
        """, (lattice_type_id,))
        row = cur.fetchone()
    return LatticeMetadata(*row) if row else None


def upsert_metadata(meta: LatticeMetadata) -> None:
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO lattice_metadata
                (lattice_type_id, coordination_number, packing_efficiency,
                 typical_materials, applications, wiki_url, notes,
                 enriched_at, enrichment_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (lattice_type_id) DO UPDATE SET
                coordination_number = EXCLUDED.coordination_number,
                packing_efficiency  = EXCLUDED.packing_efficiency,
                typical_materials   = EXCLUDED.typical_materials,
                applications        = EXCLUDED.applications,
                wiki_url            = EXCLUDED.wiki_url,
                notes               = EXCLUDED.notes,
                enriched_at         = EXCLUDED.enriched_at,
                enrichment_source   = EXCLUDED.enrichment_source
        """, (
            meta.lattice_type_id, meta.coordination_number, meta.packing_efficiency,
            meta.typical_materials, meta.applications, meta.wiki_url,
            meta.notes, meta.enriched_at or datetime.now(), meta.enrichment_source,
        ))
