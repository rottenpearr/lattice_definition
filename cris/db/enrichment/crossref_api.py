"""
CrossRef REST API — поиск научных статей по формуле/названию вещества.

Документация: https://api.crossref.org/swagger-ui/index.html
Ключ API не нужен. Polite pool: добавляем mailto в User-Agent.
Rate limit: ~50 req/s в polite pool.
"""
import requests
from typing import Optional
from cris.logger import logger

_BASE    = "https://api.crossref.org/works"
_TIMEOUT = 10
_HEADERS = {"User-Agent": "CRIS/1.0 (crystal lattice recognition; mailto:cris@research.local)"}


def search_articles(query: str, max_results: int = 5) -> list[dict]:
    """
    Ищет статьи по запросу (формула, название вещества).

    Возвращает список словарей:
        {doi, title, journal, year, url, snippet}
    """
    params = {
        "query": query,
        "rows": max_results,
        "select": "DOI,title,container-title,published,abstract,URL",
        "filter": "has-abstract:true",
        "sort": "relevance",
    }
    try:
        r = requests.get(_BASE, params=params, headers=_HEADERS, timeout=_TIMEOUT)
        if r.status_code != 200:
            logger.warning("CrossRef: HTTP {} for query '{}'", r.status_code, query)
            return []
        items = r.json().get("message", {}).get("items", [])
    except Exception as e:
        logger.warning("CrossRef request failed: {} | query={}", e, query)
        return []

    results = []
    for item in items:
        title = (item.get("title") or [""])[0]
        journal = (item.get("container-title") or [""])[0]
        doi = item.get("DOI", "")
        url = item.get("URL") or (f"https://doi.org/{doi}" if doi else "")
        abstract = item.get("abstract", "")
        # берём первые 300 символов абстракта как snippet
        snippet = abstract[:300].strip() if abstract else ""

        year = None
        pub = item.get("published", {})
        parts = pub.get("date-parts", [[]])[0]
        if parts:
            year = parts[0]

        if not title:
            continue

        results.append({
            "doi":     doi,
            "title":   title,
            "journal": journal,
            "year":    year,
            "url":     url,
            "snippet": snippet,
        })

    logger.debug("CrossRef: found {} articles for '{}'", len(results), query)
    return results
