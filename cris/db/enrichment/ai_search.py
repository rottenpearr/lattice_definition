"""
AI-обогащение через Claude API (Anthropic).
Переменная окружения: ANTHROPIC_API_KEY
"""
import json
import os
from typing import Optional
from cris.logger import logger

try:
    import anthropic
    _CLIENT = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    _AVAILABLE = bool(os.getenv("ANTHROPIC_API_KEY"))
except ImportError:
    _AVAILABLE = False
    _CLIENT = None

_MODEL = "claude-haiku-4-5-20251001"


def _ask(prompt: str, max_tokens: int = 512) -> Optional[str]:
    if not _AVAILABLE:
        return None
    try:
        msg = _CLIENT.messages.create(
            model=_MODEL, max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        logger.error("Claude API request failed: {}", e)
        return None


def enrich_lattice_type(name_en: str, name_ru: str) -> dict:
    """
    Запрашивает фактические данные об открытии типа решётки.
    Возвращает словарь для lattice_metadata.
    """
    prompt = f"""You are a crystallography expert. Provide factual information about the
{name_en} ({name_ru}) crystal lattice type as JSON:
{{
  "discoverer": "Name(s) or 'Unknown'",
  "discovery_year": integer or null,
  "discovery_context": "1-2 sentences",
  "wiki_url": "Wikipedia URL or empty string",
  "review_doi": "DOI of a key review paper or empty string",
  "notes": "1-2 interesting facts for a student"
}}
Respond ONLY with the JSON object."""
    raw = _ask(prompt, 400)
    if not raw:
        return {}
    try:
        return {k: v for k, v in json.loads(raw).items() if v not in (None, "", 0)}
    except Exception:
        return {}


def clarify_recognition(candidates: list[dict]) -> str:
    """
    Помогает разобраться, когда разные методы дали разные результаты.
    candidates: [{"method": "KDE_RF", "lattice": "cubic FCC", "confidence": 0.87}, ...]
    Возвращает объяснение на русском для отображения в UI.
    """
    prompt = f"""Crystal lattice recognition system got these results from different methods:
{json.dumps(candidates, ensure_ascii=False, indent=2)}
In 2-3 sentences in Russian, explain which result is more likely correct and why.
Be concise and scientific."""
    return _ask(prompt, 300) or ""


def describe_structure(formula: str, lattice_type: str,
                       space_group: str, doi: str = "") -> str:
    """Краткое описание вещества для UI после распознавания."""
    ref = f" (DOI: {doi})" if doi else ""
    prompt = (f"Describe {formula} with {lattice_type} lattice, "
              f"space group {space_group}{ref} in 2-3 sentences in Russian. "
              f"Focus on practical significance and key properties. Be concise.")
    return _ask(prompt, 250) or ""
