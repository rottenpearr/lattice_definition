"""
OSTI.gov API — поиск научных публикаций Министерства энергетики США.

Особенно полезен для ядерных материалов: UO2, UN, UC, PuO2 и др.
Документация: https://www.osti.gov/api/v1
Ключ API не нужен.
"""
import requests
from typing import Optional
from cris.logger import logger

_BASE    = "https://www.osti.gov/api/v1/records"
_TIMEOUT = 10
_HEADERS = {"Accept": "application/json"}


def search_articles(query: str, max_results: int = 5) -> list[dict]:
    """
    Ищет публикации по запросу в базе OSTI.gov.

    Возвращает список словарей:
        {doi, title, journal, year, url, snippet}
    """
    params = {
        "q":              query,
        "rows":           max_results,
        "sort":           "score desc",
    }
    try:
        r = requests.get(_BASE, params=params, headers=_HEADERS, timeout=_TIMEOUT)
        if r.status_code != 200:
            logger.warning("OSTI: HTTP {} for query '{}'", r.status_code, query)
            return []
        items = r.json()
        if not isinstance(items, list):
            items = items.get("records", [])
    except Exception as e:
        logger.warning("OSTI request failed: {} | query={}", e, query)
        return []

    results = []
    for item in items:
        title   = item.get("title", "").strip()
        doi     = item.get("doi", "")
        url     = item.get("site_url") or (f"https://doi.org/{doi}" if doi else "")
        journal = item.get("journal_name") or item.get("publisher_name", "")
        snippet = (item.get("description") or item.get("abstract") or "")[:300].strip()

        year = None
        pub_date = item.get("publication_date") or item.get("published_date") or ""
        if pub_date and len(pub_date) >= 4:
            try:
                year = int(pub_date[:4])
            except ValueError:
                pass

        if not title:
            continue

        results.append({
            "doi":     doi,
            "title":   title,
            "journal": journal,
            "year":    year,
            "url":     url,
            "snippet": snippet,
            "source":  "OSTI",
        })

    logger.debug("OSTI: found {} articles for '{}'", len(results), query)
    return results
