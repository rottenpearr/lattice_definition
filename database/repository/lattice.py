"""CRUD для lattice_type и lattice_metadata."""
from typing import Optional
from database.db import get_cursor
from database.models import LatticeType, LatticeMetadata


def get_all_lattice_types() -> list[LatticeType]:
    with get_cursor() as cur:
        cur.execute("SELECT id, name_en, name_ru, description, crystal_system, bravais_lattice, "
                    "space_group_number_min, space_group_number_max, point_group FROM lattice_type")
        rows = cur.fetchall()
    return [LatticeType(*row) for row in rows]


def get_lattice_type(lattice_type_id: int) -> Optional[LatticeType]:
    with get_cursor() as cur:
        cur.execute("SELECT id, name_en, name_ru, description, crystal_system, bravais_lattice, "
                    "space_group_number_min, space_group_number_max, point_group "
                    "FROM lattice_type WHERE id = %s", (lattice_type_id,))
        row = cur.fetchone()
    return LatticeType(*row) if row else None


def get_metadata(lattice_type_id: int) -> Optional[LatticeMetadata]:
    with get_cursor() as cur:
        cur.execute("SELECT id, lattice_type_id, discoverer, discovery_year, discovery_context, "
                    "wiki_url, review_doi, notes, last_enriched_at, enrichment_source "
                    "FROM lattice_metadata WHERE lattice_type_id = %s", (lattice_type_id,))
        row = cur.fetchone()
    return LatticeMetadata(*row) if row else None


def upsert_metadata(meta: LatticeMetadata) -> None:
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO lattice_metadata
                (lattice_type_id, discoverer, discovery_year, discovery_context,
                 wiki_url, review_doi, notes, last_enriched_at, enrichment_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                discoverer         = VALUES(discoverer),
                discovery_year     = VALUES(discovery_year),
                discovery_context  = VALUES(discovery_context),
                wiki_url           = VALUES(wiki_url),
                review_doi         = VALUES(review_doi),
                notes              = VALUES(notes),
                last_enriched_at   = VALUES(last_enriched_at),
                enrichment_source  = VALUES(enrichment_source)
        """, (
            meta.lattice_type_id, meta.discoverer, meta.discovery_year,
            meta.discovery_context, meta.wiki_url, meta.review_doi,
            meta.notes, meta.last_enriched_at, meta.enrichment_source,
        ))
