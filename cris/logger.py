"""
Центральный логгер проекта. Импортировать во всех модулях:
    from cris.logger import logger
"""
import sys
from pathlib import Path
from loguru import logger

_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

logger.remove()

logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
    colorize=True,
)

logger.add(
    _LOG_DIR / "cris_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} — {message}",
    rotation="00:00",     # новый файл каждый день
    retention="30 days",
    compression="zip",
    encoding="utf-8",
)
