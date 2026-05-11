"""CRUD для substance_info — описание вещества после распознавания."""
import json
from datetime import datetime
from typing import Optional

from cris.db.connection import get_cursor
from cris.db.models import SubstanceInfo


def get_by_structure(structure_id: int) -> Optional[SubstanceInfo]:
    """Возвращает описание вещества по structure_id или None."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, structure_id, description, applications, hazards,
                   properties, scientific_sources, enriched_at, enrichment_source
            FROM substance_info
            WHERE structure_id = %s
        """, (structure_id,))
        row = cur.fetchone()
    if not row:
        return None
    return SubstanceInfo(
        id=row[0],
        structure_id=row[1],
        description=row[2] or "",
        applications=row[3] or "",
        hazards=row[4] or "",
        properties=row[5],           # psycopg2 вернёт dict из JSONB
        scientific_sources=row[6],   # psycopg2 вернёт list из JSONB
        enriched_at=row[7],
        enrichment_source=row[8] or "",
    )


def upsert(info: SubstanceInfo) -> int:
    """Сохраняет или обновляет описание вещества. Возвращает id записи."""
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO substance_info
                (structure_id, description, applications, hazards,
                 properties, scientific_sources, enriched_at, enrichment_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (structure_id) DO UPDATE SET
                description        = EXCLUDED.description,
                applications       = EXCLUDED.applications,
                hazards            = EXCLUDED.hazards,
                properties         = EXCLUDED.properties,
                scientific_sources = EXCLUDED.scientific_sources,
                enriched_at        = EXCLUDED.enriched_at,
                enrichment_source  = EXCLUDED.enrichment_source
            RETURNING id
        """, (
            info.structure_id,
            info.description,
            info.applications,
            info.hazards,
            json.dumps(info.properties, ensure_ascii=False) if info.properties else None,
            json.dumps(info.scientific_sources, ensure_ascii=False) if info.scientific_sources else None,
            info.enriched_at or datetime.now(),
            info.enrichment_source,
        ))
        return cur.fetchone()[0]
