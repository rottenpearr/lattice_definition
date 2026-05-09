"""
AI-поиск через Claude API для обогащения метаданных.

Использует Anthropic SDK для:
1. Поиска информации об открытии типа решётки (кто, когда, как)
2. Краткого резюме по конкретному веществу
3. Уточнения результатов распознавания (если несколько вариантов близки)

Требует переменную окружения ANTHROPIC_API_KEY.
"""
import os
from typing import Optional

try:
    import anthropic
    _CLIENT = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    _CLIENT = None


_MODEL = "claude-haiku-4-5-20251001"   # быстрый и дешёвый для фактологических запросов


def _ask(prompt: str, max_tokens: int = 512) -> Optional[str]:
    if not _AVAILABLE or not os.getenv("ANTHROPIC_API_KEY"):
        return None
    try:
        msg = _CLIENT.messages.create(
            model=_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        print(f"[AI] Ошибка запроса к Claude: {e}")
        return None


def enrich_lattice_type(name_en: str, name_ru: str) -> dict:
    """
    Запрашивает у Claude краткие факты о типе решётки.
    Возвращает словарь с полями для lattice_metadata.
    """
    prompt = f"""You are a crystallography expert. Provide factual information about the
{name_en} ({name_ru}) crystal lattice type in JSON format:
{{
  "discoverer": "Name(s) of discoverer(s) or 'Unknown'",
  "discovery_year": integer year or null,
  "discovery_context": "1-2 sentences about how/when it was discovered",
  "wiki_url": "Wikipedia URL or empty string",
  "review_doi": "DOI of a key review paper or empty string",
  "notes": "1-2 interesting facts for a student"
}}
Respond ONLY with the JSON object, no markdown, no extra text."""

    raw = _ask(prompt, max_tokens=400)
    if not raw:
        return {}
    try:
        import json
        data = json.loads(raw)
        return {k: v for k, v in data.items() if v not in (None, "", 0)}
    except Exception:
        return {}


def clarify_recognition(candidates: list[dict]) -> str:
    """
    Когда несколько методов дали разные результаты, просим Claude помочь разобраться.

    candidates: список словарей вида
        [{"method": "KDE_RF", "lattice": "cubic FCC", "confidence": 0.87},
         {"method": "KDE_DNN", "lattice": "cubic BCC", "confidence": 0.79}]

    Возвращает строку-объяснение для отображения пользователю.
    """
    import json
    prompt = f"""A crystal lattice recognition system got these results from different methods:
{json.dumps(candidates, ensure_ascii=False, indent=2)}

In 2-3 sentences in Russian, explain which result is more likely correct and why.
Be concise, scientific, helpful to a student."""

    return _ask(prompt, max_tokens=300) or ""


def summarize_substance(formula: str, lattice_type: str,
                        space_group: str, doi: str = "") -> str:
    """
    Краткое описание вещества для вывода в UI после распознавания.
    """
    ref = f" (source DOI: {doi})" if doi else ""
    prompt = f"""Describe the substance {formula} with {lattice_type} lattice,
space group {space_group}{ref} in 2-3 sentences in Russian.
Focus on practical significance and key physical properties. Be concise."""

    return _ask(prompt, max_tokens=250) or ""
