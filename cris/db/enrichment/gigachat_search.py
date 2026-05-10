"""
AI-обогащение через GigaChat API (Сбер).

Переменные окружения:
    GIGACHAT_CREDENTIALS — строка авторизации из личного кабинета
                           https://developers.sber.ru/studio/workspaces
    GIGACHAT_SCOPE       — GIGACHAT_API_PERS (физлицо) или
                           GIGACHAT_API_CORP (корпоратив), по умолчанию PERS
    GIGACHAT_MODEL       — модель: GigaChat / GigaChat-Plus / GigaChat-Pro
                           по умолчанию GigaChat
"""
import json
import os
from typing import Optional
from cris.logger import logger

try:
    from gigachat import GigaChat
    from gigachat.models import Chat, Messages, MessagesRole
    _GIGACHAT_AVAILABLE = True
except ImportError:
    _GIGACHAT_AVAILABLE = False
    logger.warning("gigachat package not installed. Run: pip install gigachat")

_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS", "")
_SCOPE       = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
_MODEL       = os.getenv("GIGACHAT_MODEL", "GigaChat-2-Max")
_AVAILABLE   = _GIGACHAT_AVAILABLE and bool(_CREDENTIALS)


def _ask(prompt: str, max_tokens: int = 512) -> Optional[str]:
    """Отправляет запрос в GigaChat, возвращает текст ответа или None."""
    if not _AVAILABLE:
        return None
    try:
        payload = Chat(
            model=_MODEL,
            messages=[Messages(role=MessagesRole.USER, content=prompt)],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        with GigaChat(
            credentials=_CREDENTIALS,
            scope=_SCOPE,
            verify_ssl_certs=False,   # Сбер использует собственный CA
        ) as giga:
            response = giga.chat(payload)
            return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("GigaChat API request failed: {}", e)
        return None


def enrich_lattice_type(name_en: str, name_ru: str) -> dict:
    """
    Запрашивает структурные и физические данные о типе решётки.
    Возвращает словарь для lattice_metadata.
    """
    prompt = f"""Ты эксперт по кристаллографии. Дай точные структурные данные о типе кристаллической решётки
{name_en} ({name_ru}) строго в формате JSON:
{{
  "coordination_number": целое число (сколько ближайших соседей у атома),
  "packing_efficiency": число от 0 до 1 (доля занятого объёма),
  "typical_materials": "примеры веществ через запятую: Al, Cu, Fe...",
  "applications": "1-2 предложения о практическом применении",
  "wiki_url": "ссылка на англоязычную Википедию или пустая строка",
  "notes": "1-2 интересных структурных факта"
}}
Отвечай ТОЛЬКО JSON-объектом без лишнего текста."""
    raw = _ask(prompt, 400)
    if not raw:
        return {}
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return {k: v for k, v in json.loads(raw).items() if v not in (None, "", 0)}
    except Exception as e:
        logger.warning("GigaChat: failed to parse JSON response: {} | raw: {}", e, raw[:200])
        return {}


def clarify_recognition(candidates: list[dict]) -> str:
    """
    Помогает разобраться, когда разные методы дали разные результаты.
    candidates: [{"method": "KDE_RF", "lattice": "cubic FCC", "confidence": 0.87}, ...]
    Возвращает объяснение на русском для отображения в UI.
    """
    prompt = f"""Система распознавания кристаллических решёток получила следующие результаты от разных методов:
{json.dumps(candidates, ensure_ascii=False, indent=2)}
В 2-3 предложениях объясни, какой результат скорее всего верен и почему.
Будь краток и научен."""
    return _ask(prompt, 300) or ""


def describe_structure(formula: str, lattice_type: str,
                       space_group: str, doi: str = "") -> str:
    """Краткое описание вещества для UI после распознавания."""
    ref = f" (DOI: {doi})" if doi else ""
    prompt = (f"Опиши вещество {formula} с решёткой типа {lattice_type}, "
              f"пространственная группа {space_group}{ref} в 2-3 предложениях. "
              f"Сосредоточься на практическом значении и ключевых свойствах. Будь краток.")
    return _ask(prompt, 250) or ""


def describe_substance(
    formula: str,
    name: str = "",
    lattice_type: str = "",
    properties: dict = None,
    articles: list = None,
) -> dict:
    """
    Генерирует структурированное описание вещества на основе собранных данных.
    Используется substance_enricher после PubChem + CrossRef.

    Возвращает словарь:
        {description, applications, hazards}
    """
    props_text = ""
    if properties:
        lines = []
        for k, v in properties.items():
            if k != "pubchem_cid":
                lines.append(f"  {k}: {v}")
        if lines:
            props_text = "Известные свойства из PubChem:\n" + "\n".join(lines)

    articles_text = ""
    if articles:
        titles = [f"  - {a['title']} ({a.get('journal','')}, {a.get('year','')})"
                  for a in articles[:3]]
        articles_text = "Найденные научные публикации:\n" + "\n".join(titles)

    lattice_ctx = f" с кристаллической решёткой типа {lattice_type}" if lattice_type else ""
    name_ctx = f" ({name})" if name and name != formula else ""

    prompt = f"""Ты эксперт по материаловедению и кристаллографии.
Вещество: {formula}{name_ctx}{lattice_ctx}.
{props_text}
{articles_text}

На основе этих данных дай ответ строго в формате JSON:
{{
  "description": "2-3 предложения: что это за вещество, его кристаллическая структура и ключевые свойства",
  "applications": "1-2 предложения: где применяется в науке и промышленности",
  "hazards": "токсичность, радиоактивность, взрывоопасность или пустая строка если не опасно"
}}
Отвечай ТОЛЬКО JSON-объектом без лишнего текста."""

    raw = _ask(prompt, 500)
    if not raw:
        return {}
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return {k: v for k, v in json.loads(raw).items() if v not in (None, "")}
    except Exception as e:
        logger.warning("GigaChat describe_substance: failed to parse JSON: {} | raw: {}", e, raw[:200])
        return {}
