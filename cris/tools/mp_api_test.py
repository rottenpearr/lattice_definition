"""Тестовый запрос к Materials Project API. Ключ задаётся через MP_API_KEY."""
from cris.db.enrichment.mp_api import search

results = search("U2C3")
for entry in results:
    print(entry)
