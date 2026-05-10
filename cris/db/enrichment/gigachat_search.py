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
    Запрашивает фактические данные об открытии типа решётки.
    Возвращает словарь для lattice_metadata.
    """
    prompt = f"""Ты эксперт по кристаллографии. Дай фактические данные о типе кристаллической решётки
{name_en} ({name_ru}) строго в формате JSON:
{{
  "discoverer": "Имя(а) первооткрывателя или 'Unknown'",
  "discovery_year": целое число или null,
  "discovery_context": "1-2 предложения об условиях открытия",
  "wiki_url": "ссылка на Википедию или пустая строка",
  "review_doi": "DOI обзорной статьи или пустая строка",
  "notes": "1-2 интересных факта для студента"
}}
Отвечай ТОЛЬКО JSON-объектом без лишнего текста."""
    raw = _ask(prompt, 500)
    if not raw:
        return {}
    # GigaChat иногда оборачивает JSON в ```json ... ``` — чистим
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
