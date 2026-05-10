"""
Оркестратор обогащения вещества после распознавания.

Пайплайн:
    1. PubChem     → физико-химические свойства (плотность, т°пл, цвет...)
    2. CrossRef    → топ-5 научных статей по формуле + типу решётки
    3. GigaChat    → связный текст-описание на основе собранных данных
    4. substance_info → сохраняем всё в БД (upsert)

Пример использования:
    from cris.db.enrichment.substance_enricher import enrich_substance
    enrich_substance(structure_id=1, formula="UO2", lattice_type="cubic")
"""
import json
from datetime import datetime

from cris.logger import logger
from cris.db.models import SubstanceInfo
from cris.db.repository.substance import get_by_structure, upsert
from cris.db.enrichment.pubchem_api import get_properties
from cris.db.enrichment.crossref_api import search_articles
from cris.db.enrichment import gigachat_search


def enrich_substance(
    structure_id: int,
    formula: str,
    lattice_type: str = "",
    force: bool = False,
) -> bool:
    """
    Обогащает substance_info для указанной структуры.

    Args:
        structure_id: ID в таблице reference_structure
        formula:      химическая формула ("UO2", "NaCl", "Fe")
        lattice_type: название типа решётки для контекста поиска
        force:        перезаписать, если данные уже есть

    Returns:
        True если обогащение прошло успешно
    """
    if not force and get_by_structure(structure_id) is not None:
        logger.debug("substance_info already exists for structure_id={}, skipping", structure_id)
        return True

    sources_used = []

    # ── 1. PubChem: физические свойства ──────────────────────────────────
    properties = {}
    pubchem_data = get_properties(formula)
    if pubchem_data:
        properties = pubchem_data
        sources_used.append("PUBCHEM")
        logger.debug("PubChem: {} props for {}", len(pubchem_data), formula)

    # ── 2. CrossRef: научные статьи ───────────────────────────────────────
    scientific_sources = []
    query = f"{formula} crystal structure"
    if lattice_type:
        query += f" {lattice_type}"

    articles = search_articles(query, max_results=5)
    if articles:
        scientific_sources = articles
        sources_used.append("CROSSREF")
        logger.debug("CrossRef: {} articles for '{}'", len(articles), query)

    # ── 3. GigaChat: связный текст ────────────────────────────────────────
    description = ""
    applications = ""
    hazards = ""

    ai_result = gigachat_search.describe_substance(
        formula=formula,
        lattice_type=lattice_type,
        properties=properties,
        articles=scientific_sources,
    )
    if ai_result:
        description  = ai_result.get("description", "")
        applications = ai_result.get("applications", "")
        hazards      = ai_result.get("hazards", "")
        sources_used.append("AI")

    if not description and not properties and not scientific_sources:
        logger.warning("substance_enricher: no data found for '{}'", formula)
        return False

    # ── 4. Сохраняем ─────────────────────────────────────────────────────
    info = SubstanceInfo(
        id=None,
        structure_id=structure_id,
        description=description,
        applications=applications,
        hazards=hazards,
        properties=properties or None,
        scientific_sources=scientific_sources or None,
        enriched_at=datetime.now(),
        enrichment_source="+".join(sources_used),
    )
    upsert(info)
    logger.info("Substance enriched: '{}' (sources: {})", formula, info.enrichment_source)
    return True
