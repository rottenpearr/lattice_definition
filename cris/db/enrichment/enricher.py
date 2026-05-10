"""
Оркестратор обогащения: COD + Materials Project + AI.

AI-провайдер выбирается через переменную окружения AI_PROVIDER:
    AI_PROVIDER=gigachat   — GigaChat (Сбер), нужен GIGACHAT_CREDENTIALS
    AI_PROVIDER=claude     — Claude (Anthropic), нужен ANTHROPIC_API_KEY
    AI_PROVIDER=auto       — сначала GigaChat, при неудаче Claude (по умолчанию)

Примеры:
    from cris.db.enrichment.enricher import enrich_lattice_type, enrich_structure
    enrich_lattice_type(lattice_type_id=8)       # кубическая
    enrich_structure(structure_id=1, formula="NaCl")
"""
import json
import os
from datetime import datetime

from cris.logger import logger
from cris.db.connection import get_cursor
from cris.db.repository.lattice import get_by_id as get_lattice, upsert_metadata
from cris.db.repository.structure import update_external_ids
from cris.db.models import LatticeMetadata
from cris.db.enrichment.cod_api import search as cod_search
from cris.db.enrichment.mp_api import search as mp_search
from cris.db.enrichment.robocrys_describer import describe_and_save

# ── Выбор AI-провайдера ───────────────────────────────────────────────────────
_AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").lower()

def _get_ai_enrich_fn():
    """Возвращает функцию enrich_lattice_type нужного провайдера."""
    if _AI_PROVIDER == "gigachat":
        from cris.db.enrichment.gigachat_search import enrich_lattice_type
        return enrich_lattice_type
    if _AI_PROVIDER == "claude":
        from cris.db.enrichment.ai_search import enrich_lattice_type
        return enrich_lattice_type
    # auto: пробуем GigaChat, если вернул пустой dict — Claude
    from cris.db.enrichment import gigachat_search, ai_search
    def _auto(name_en, name_ru):
        result = gigachat_search.enrich_lattice_type(name_en, name_ru)
        if result:
            logger.debug("AI provider used: GigaChat")
            return result
        logger.debug("GigaChat returned nothing, falling back to Claude")
        return ai_search.enrich_lattice_type(name_en, name_ru)
    return _auto

_ai_enrich_lattice = _get_ai_enrich_fn()


def _log(source: str, target_type: str, target_id: int,
         query: str, summary: str, enriched: dict,
         status: int, success: bool) -> None:
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO external_lookup_log
                (source, target_type, target_id, query_text,
                 result_summary, enriched_fields, http_status, is_successful)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (source, target_type, target_id, query, summary,
              json.dumps(enriched, ensure_ascii=False), status, success))


def enrich_lattice_type(lattice_type_id: int) -> bool:
    """Обогащает lattice_metadata через AI. Возвращает True при успехе."""
    lt = get_lattice(lattice_type_id)
    if not lt:
        return False
    data = _ai_enrich_lattice(lt.name_en, lt.name_ru)
    if not data:
        _log("AI_SEARCH", "lattice_type", lattice_type_id,
             f"enrich {lt.name_en}", "", {}, 0, False)
        return False
    upsert_metadata(LatticeMetadata(
        lattice_type_id=lattice_type_id,
        discoverer=data.get("discoverer", ""),
        discovery_year=data.get("discovery_year"),
        discovery_context=data.get("discovery_context", ""),
        wiki_url=data.get("wiki_url", ""),
        review_doi=data.get("review_doi", ""),
        notes=data.get("notes", ""),
        enriched_at=datetime.now(),
        enrichment_source="AI_SEARCH",
    ))
    _log("AI_SEARCH", "lattice_type", lattice_type_id,
         f"enrich {lt.name_en}", str(data), data, 200, True)
    logger.info("Lattice metadata enriched via AI: '{}'", lt.name_ru)
    return True


def enrich_structure(structure_id: int, formula: str,
                     sg_number: int = 0,
                     cif_path: str = "") -> bool:
    """
    Ищет вещество в COD и MP, обновляет внешние ID.
    Если передан cif_path — генерирует описание через robocrystallographer.
    """
    success = False
    mp_id = ""

    cod_results = cod_search(formula, sg_number or None)
    if cod_results:
        best = cod_results[0]
        update_external_ids(structure_id, cod_id=best.cod_id,
                            doi=best.doi, source_url=best.entry_url)
        _log("COD", "reference_structure", structure_id,
             f"formula={formula}", f"cod={best.cod_id}",
             {"cod_id": best.cod_id, "doi": best.doi}, 200, True)
        success = True
    else:
        _log("COD", "reference_structure", structure_id,
             f"formula={formula}", "not found", {}, 200, False)

    mp_results = mp_search(formula)
    if mp_results:
        best_mp = mp_results[0]
        mp_id = best_mp.mp_id
        update_external_ids(structure_id, mp_id=mp_id)
        _log("MATERIALS_PROJECT", "reference_structure", structure_id,
             f"formula={formula}", f"mp_id={mp_id}",
             {"mp_id": mp_id}, 200, True)
        success = True
    else:
        _log("MATERIALS_PROJECT", "reference_structure", structure_id,
             f"formula={formula}", "not found", {}, 200, False)

    # генерируем структурное описание через robocrystallographer
    describe_and_save(structure_id, cif_path=cif_path, mp_id=mp_id)

    return success
