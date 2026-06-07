"""
CRIS — красивый отчёт по ML-моделям для XYZ-файла.

Запуск:
    python cris_report.py                        # NaCl из датасета
    python cris_report.py path/to/file.xyz
"""

import sys
import os

# Форсируем UTF-8 на Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
from cris import identify, load_xyz

# ── ANSI-цвета ────────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"
BLUE   = "\033[94m"
MAGENTA = "\033[95m"

W = 54  # ширина блока

def bar(conf: float, width: int = 20) -> str:
    filled = round(conf * width)
    empty  = width - filled
    return GREEN + "█" * filled + GRAY + "░" * empty + RESET

def header_box(title: str, color: str = CYAN) -> str:
    inner = f"  {title}  "
    pad   = W - len(inner) - 2
    return (
        f"\n{color}{BOLD}┌{'─' * (W - 2)}┐{RESET}\n"
        f"{color}{BOLD}│{inner}{'':>{pad}}│{RESET}\n"
        f"{color}{BOLD}└{'─' * (W - 2)}┘{RESET}"
    )

def row(rank: int, name: str, conf: float) -> str:
    medal  = ["", "  1.", "  2.", "  3."][rank]
    color  = GREEN if rank == 1 else (YELLOW if rank == 2 else WHITE)
    badge  = f" ← топ" if rank == 1 else ""
    return (
        f"{color}{BOLD}{medal}{RESET} "
        f"{color}{name:<26}{RESET} "
        f"{bar(conf)}  "
        f"{color}{BOLD}{conf:>5.1%}{RESET}"
        f"{GRAY}{badge}{RESET}"
    )

def divider() -> str:
    return GRAY + "  " + "─" * (W - 2) + RESET

# ── Входной файл ──────────────────────────────────────────────────────────────
xyz_path = Path(sys.argv[1]) if len(sys.argv) > 1 \
           else Path(__file__).parent / "data" / "db" / "xyz" / "1000041.xyz"

if not xyz_path.exists():
    print(f"Файл не найден: {xyz_path}")
    sys.exit(1)

sites = load_xyz(xyz_path)

# ── Запуск ────────────────────────────────────────────────────────────────────
# Подавляем WARNING-и из логгера чтобы не засорять вывод
import logging
logging.disable(logging.WARNING)
os.environ["LOGURU_LEVEL"] = "ERROR"

result = identify(sites)

# ── Шапка ─────────────────────────────────────────────────────────────────────
print()
print(f"{CYAN}{BOLD}{'═' * W}{RESET}")
print(f"{CYAN}{BOLD}  CRIS · Crystal Recognition Report{' ' * (W - 37)}{RESET}")
print(f"{CYAN}{BOLD}{'═' * W}{RESET}")
print(f"{DIM}  Файл   : {xyz_path.name}{RESET}")
print(f"{DIM}  Атомов : {len(sites)}{RESET}")
print(f"{CYAN}{BOLD}{'═' * W}{RESET}")

# Достаём предсказания по методам
preds_by_method = {e["method"]: e["predictions"] for e in result.ml_results}

# ── CatBoost · Сингония ───────────────────────────────────────────────────────
cb_lattice = preds_by_method.get("catboost", [])
print(header_box("CatBoost  ·  Сингония (тип решётки)", BLUE))
if cb_lattice:
    for i, p in enumerate(cb_lattice[:3], 1):
        name = p.get("class", p.get("lattice_name", "?"))
        print(row(i, name, p["confidence"]))
        if i < len(cb_lattice[:3]):
            print(divider())
else:
    print(f"  {GRAY}нет данных{RESET}")

# ── CatBoost · Вещество ───────────────────────────────────────────────────────
cb_subst = preds_by_method.get("catboost_substance", [])
print(header_box("CatBoost  ·  Вещество", MAGENTA))
if cb_subst:
    for i, p in enumerate(cb_subst[:3], 1):
        name = p.get("class", "?")
        print(row(i, name, p["confidence"]))
        if i < len(cb_subst[:3]):
            print(divider())
else:
    print(f"  {GRAY}нет данных{RESET}")

# ── Random Forest · Вещество ──────────────────────────────────────────────────
rf = preds_by_method.get("rf", [])
print(header_box("Random Forest  ·  Вещество", YELLOW))
if rf:
    for i, p in enumerate(rf[:3], 1):
        name = p.get("class", "?")
        print(row(i, name, p["confidence"]))
        if i < len(rf[:3]):
            print(divider())
else:
    print(f"  {GRAY}нет данных{RESET}")

# ── Итог ──────────────────────────────────────────────────────────────────────
print(f"\n{CYAN}{BOLD}{'═' * W}{RESET}")
print(f"{CYAN}{BOLD}  Итог{RESET}")
print(f"{CYAN}{BOLD}{'─' * W}{RESET}")
if result.lattice_type:
    print(f"  {WHITE}Тип решётки :{RESET} {GREEN}{BOLD}{result.lattice_type}{RESET}  "
          f"{DIM}({result.lattice_confidence:.0%}){RESET}")
if result.substance:
    print(f"  {WHITE}Вещество    :{RESET} {GREEN}{BOLD}{result.substance}{RESET}  "
          f"{DIM}({result.substance_confidence:.0%}){RESET}")
print(f"{CYAN}{BOLD}{'═' * W}{RESET}\n")
