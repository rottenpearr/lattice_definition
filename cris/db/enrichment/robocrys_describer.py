"""
Генератор текстовых описаний кристаллических структур через Robocrystallographer.
https://github.com/hackingmaterials/robocrystallographer

Два источника структуры:
  - локальный CIF файл (работает без интернета)
  - Materials Project по mp_id (нужен MP_API_KEY)

Результат сохраняется в поле structure_description таблицы reference_structure.
"""
from pathlib import Path
from typing import Optional

from cris.logger import logger

try:
    from robocrys import StructureCondenser, StructureDescriber
    _ROBOCRYS_AVAILABLE = True
except ImportError:
    _ROBOCRYS_AVAILABLE = False
    logger.warning("robocrys not installed — run: pip install robocrys")

try:
    from pymatgen.core import Structure
    _PYMATGEN_AVAILABLE = True
except ImportError:
    _PYMATGEN_AVAILABLE = False


def _check_deps() -> bool:
    if not _ROBOCRYS_AVAILABLE or not _PYMATGEN_AVAILABLE:
        logger.error("robocrys or pymatgen not available")
        return False
    return True


def describe_from_cif(cif_path: str) -> Optional[str]:
    """
    Генерирует описание структуры из локального CIF файла.
    cif_path — путь относительно корня проекта или абсолютный.
    """
    if not _check_deps():
        return None
    path = Path(cif_path)
    if not path.exists():
        logger.error("CIF file not found: {}", cif_path)
        return None
    try:
        structure = Structure.from_file(str(path))
        return _describe(structure)
    except Exception as e:
        logger.error("Failed to describe structure from CIF {}: {}", cif_path, e)
        return None


def describe_from_mp(mp_id: str) -> Optional[str]:
    """
    Генерирует описание структуры, загружая её из Materials Project.
    Требует переменную окружения MP_API_KEY.
    """
    if not _check_deps():
        return None
    import os
    api_key = os.getenv("MP_API_KEY", "")
    if not api_key:
        logger.warning("MP_API_KEY not set — cannot fetch structure for {}", mp_id)
        return None
    try:
        from mp_api.client import MPRester
        with MPRester(api_key) as mpr:
            structure = mpr.get_structure_by_material_id(mp_id)
        return _describe(structure)
    except Exception as e:
        logger.error("Failed to describe structure from MP {}: {}", mp_id, e)
        return None


def _describe(structure) -> Optional[str]:
    condenser = StructureCondenser()
    describer = StructureDescriber()
    condensed = condenser.condense_structure(structure)
    return describer.describe(condensed)


# ─── сохранение результата в БД ──────────────────────────────────────────────

def describe_and_save(structure_id: int, cif_path: str = "",
                      mp_id: str = "") -> Optional[str]:
    """
    Генерирует описание и сохраняет в reference_structure.structure_description.
    Пробует CIF первым (нет зависимости от интернета), потом MP.
    Возвращает текст описания или None.
    """
    description = None

    if cif_path:
        description = describe_from_cif(cif_path)
    if description is None and mp_id:
        description = describe_from_mp(mp_id)

    if description:
        _save_description(structure_id, description)
        logger.info("Structure {} description saved ({} chars)", structure_id, len(description))
    else:
        logger.warning("Could not generate description for structure_id={}", structure_id)

    return description


def _save_description(structure_id: int, description: str) -> None:
    from cris.db.connection import get_cursor
    with get_cursor() as cur:
        cur.execute(
            "UPDATE reference_structure SET structure_description = %s WHERE id = %s",
            (description, structure_id)
        )
