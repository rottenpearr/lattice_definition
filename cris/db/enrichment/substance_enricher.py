"""
Оркестратор обогащения вещества после распознавания.

Пайплайн:
    1. CrossRef    → топ-5 научных статей по формуле + типу решётки
    2. OSTI        → публикации DOE (особенно полезно для ядерных материалов)
    3. GigaChat    → связный текст-описание на основе собранных данных
    4. substance_info → сохраняем всё в БД (upsert)

Пример использования:
    from cris.db.enrichment.substance_enricher import enrich_substance
    enrich_substance(structure_id=1, formula="UO2", name="Uranium dioxide", lattice_type="cubic")
"""
from datetime import datetime

from cris.logger import logger
from cris.db.connection import get_cursor
from cris.db.models import SubstanceInfo
from cris.db.repository.substance import get_by_structure, upsert
from cris.db.enrichment.crossref_api import search_articles as crossref_search
from cris.db.enrichment.osti_api import search_articles as osti_search
from cris.db.enrichment import gigachat_search


def _load_crystal_properties(structure_id: int) -> dict:
    """Загружает кристаллографические параметры из reference_structure."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT cell_length_a, cell_length_b, cell_length_c, cell_volume,
                   cell_angle_alpha, cell_angle_beta, cell_angle_gamma,
                   sg_number, sg_hall, sg_hm, cod_id
            FROM reference_structure WHERE id = %s
        """, (structure_id,))
        row = cur.fetchone()
    if not row:
        return {}
    _int_fields  = {"sg_number", "cod_id"}
    _float_fields = {"cell_length_a", "cell_length_b", "cell_length_c", "cell_volume",
                     "cell_angle_alpha", "cell_angle_beta", "cell_angle_gamma"}
    keys = ["cell_length_a", "cell_length_b", "cell_length_c", "cell_volume",
            "cell_angle_alpha", "cell_angle_beta", "cell_angle_gamma",
            "sg_number", "sg_hall", "sg_hm", "cod_id"]
    result = {}
    for k, v in zip(keys, row):
        if v is None:
            continue
        if k in _int_fields:
            result[k] = int(v)
        elif k in _float_fields:
            result[k] = round(float(v), 6)
        else:
            result[k] = v
    return result


def enrich_substance(
    structure_id: int,
    formula: str,
    name: str = "",
    lattice_type: str = "",
    force: bool = False,
) -> bool:
    """
    Обогащает substance_info для указанной структуры.

    Args:
        structure_id: ID в таблице reference_structure
        formula:      химическая формула ("UO2", "NaCl", "Fe")
        name:         полное название вещества ("Uranium dioxide", "Sodium chloride")
        lattice_type: название типа решётки для контекста поиска
        force:        перезаписать, если данные уже есть
    """
    if not force and get_by_structure(structure_id) is not None:
        logger.debug("substance_info already exists for structure_id={}, skipping", structure_id)
        return True

    display_name = name or formula
    sources_used = []

    # ── 0. Кристаллографические параметры из reference_structure ─────────
    properties = _load_crystal_properties(structure_id)
    if properties:
        sources_used.append("COD_PARAMS")
        logger.debug("Crystal properties loaded: {} fields for id={}", len(properties), structure_id)

    # ── 1. CrossRef: научные статьи ───────────────────────────────────────
    scientific_sources = []

    crossref_query = f"{display_name} crystal structure"
    if lattice_type:
        crossref_query += f" {lattice_type}"

    crossref_articles = crossref_search(crossref_query, max_results=5)
    if crossref_articles:
        scientific_sources.extend(crossref_articles)
        sources_used.append("CROSSREF")
        logger.debug("CrossRef: {} articles for '{}'", len(crossref_articles), crossref_query)

    # ── 3. OSTI: публикации DOE ───────────────────────────────────────────
    osti_query = f"{display_name} {formula} crystal structure"
    osti_articles = osti_search(osti_query, max_results=5)
    if osti_articles:
        # дедупликация по doi
        existing_dois = {a["doi"] for a in scientific_sources if a.get("doi")}
        new_articles = [a for a in osti_articles if a.get("doi") not in existing_dois]
        if new_articles:
            scientific_sources.extend(new_articles)
            sources_used.append("OSTI")
            logger.debug("OSTI: {} new articles for '{}'", len(new_articles), osti_query)

    # ── 4. GigaChat: связный текст ────────────────────────────────────────
    description = ""
    applications = ""
    hazards = ""

    ai_result = gigachat_search.describe_substance(
        formula=formula,
        name=display_name,
        lattice_type=lattice_type,
        articles=scientific_sources[:6],  # не больше 6 статей в промпт
    )
    if ai_result:
        description  = ai_result.get("description", "")
        applications = ai_result.get("applications", "")
        hazards      = ai_result.get("hazards", "")
        sources_used.append("AI")

    if not description and not scientific_sources and not properties:
        logger.warning("substance_enricher: no data found for '{}'", display_name)
        return False

    # ── 5. Сохраняем ─────────────────────────────────────────────────────
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
    logger.info("Substance enriched: '{}' (sources: {})", display_name, info.enrichment_source)
    return True
