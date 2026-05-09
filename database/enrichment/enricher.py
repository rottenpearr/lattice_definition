"""
Оркестратор обогащения — объединяет COD, Materials Project и AI.

Пример использования:
    from database.enrichment.enricher import enrich_substance, enrich_lattice_type_metadata

    enrich_lattice_type_metadata(lattice_type_id=8)   # кубическая
    enrich_substance(substance_id=42, formula="NaCl")
"""
import json
from datetime import datetime

from database.db import get_cursor
from database.repository.lattice import get_lattice_type, upsert_metadata
from database.repository.structure import update_structure_external_ids
from database.models import LatticeMetadata
from database.enrichment.cod_api import search_by_formula
from database.enrichment.mp_api import search_by_formula as mp_search
from database.enrichment.ai_search import enrich_lattice_type, summarize_substance


def _log_lookup(source: str, target_type: str, target_id: int,
                query: str, summary: str, enriched: dict,
                status: int, success: bool) -> None:
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO external_lookup_log
                (source, target_type, target_id, query_text, result_summary,
                 enriched_fields, http_status, is_successful)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (source, target_type, target_id, query, summary,
              json.dumps(enriched, ensure_ascii=False), status, success))


def enrich_lattice_type_metadata(lattice_type_id: int, force: bool = False) -> bool:
    """
    Обогащает lattice_metadata для указанного типа решётки через AI.
    Пропускает, если данные уже есть и force=False.
    Возвращает True при успехе.
    """
    lt = get_lattice_type(lattice_type_id)
    if not lt:
        print(f"[Enricher] Тип решётки {lattice_type_id} не найден")
        return False

    ai_data = enrich_lattice_type(lt.name_en, lt.name_ru)
    if not ai_data:
        _log_lookup("AI_SEARCH", "lattice_type", lattice_type_id,
                    f"enrich {lt.name_en}", "", {}, 0, False)
        return False

    meta = LatticeMetadata(
        id=0,
        lattice_type_id=lattice_type_id,
        discoverer=ai_data.get("discoverer", ""),
        discovery_year=ai_data.get("discovery_year"),
        discovery_context=ai_data.get("discovery_context", ""),
        wiki_url=ai_data.get("wiki_url", ""),
        review_doi=ai_data.get("review_doi", ""),
        notes=ai_data.get("notes", ""),
        last_enriched_at=datetime.now(),
        enrichment_source="AI_SEARCH",
    )
    upsert_metadata(meta)

    _log_lookup("AI_SEARCH", "lattice_type", lattice_type_id,
                f"enrich {lt.name_en}", str(ai_data), ai_data, 200, True)
    print(f"[Enricher] Метаданные для '{lt.name_ru}' обновлены через AI")
    return True


def enrich_substance(substance_id: int, formula: str,
                     space_group_number: int = 0) -> bool:
    """
    Ищет вещество в COD и Materials Project, обновляет внешние ID и DOI.
    Возвращает True если хотя бы один источник дал результат.
    """
    success = False

    # --- COD ---
    cod_results = search_by_formula(formula, space_group_number or None)
    if cod_results:
        best = cod_results[0]
        update_structure_external_ids(
            substance_id,
            cod_id=best.cod_id,
            doi=best.doi,
            source_url=best.entry_url,
        )
        _log_lookup("COD", "substance", substance_id,
                    f"formula={formula}", f"COD:{best.cod_id} doi={best.doi}",
                    {"cod_id": best.cod_id, "doi": best.doi}, 200, True)
        success = True
    else:
        _log_lookup("COD", "substance", substance_id,
                    f"formula={formula}", "not found", {}, 200, False)

    # --- Materials Project ---
    mp_results = mp_search(formula)
    if mp_results:
        best_mp = mp_results[0]
        update_structure_external_ids(substance_id, mp_id=best_mp.mp_id)
        _log_lookup("MATERIALS_PROJECT", "substance", substance_id,
                    f"formula={formula}", f"mp_id={best_mp.mp_id}",
                    {"mp_id": best_mp.mp_id}, 200, True)
        success = True
    else:
        _log_lookup("MATERIALS_PROJECT", "substance", substance_id,
                    f"formula={formula}", "not found", {}, 200, False)

    return success


def get_substance_description(substance_id: int, formula: str,
                               lattice_type_name: str, space_group: str) -> str:
    """
    Возвращает AI-сгенерированное описание для отображения в UI.
    Сначала проверяет, есть ли DOI в БД (для более точного запроса).
    """
    with get_cursor() as cur:
        cur.execute("SELECT doi FROM substances WHERE id = %s", (substance_id,))
        row = cur.fetchone()
    doi = row[0] if row and row[0] else ""

    return summarize_substance(formula, lattice_type_name, space_group, doi)
