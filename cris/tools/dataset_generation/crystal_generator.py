"""
Генератор кристаллических структур — все 14 типов решёток Браве.

Поддерживает:
  • Одноатомные структуры (один вид атомов на узлах решётки)
  • Многоатомные структуры через мотив (произвольный список атомов +
    дробные координаты в ячейке) — включая диатомные типа rock-salt
    (NaCl, UN, UC), флюорит (UO2), перовскит и другие
  • Суперячейки произвольного размера через pymatgen
  • Гауссовый шум и вакансии
  • Параллельную генерацию нескольких сэмплов (multiprocessing)
  • Набор пресетов популярных соединений (--preset NaCl, UN, UC, ...)

━━━ Справка ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # Список всех типов решёток и пресетов
  python cris/tools/dataset_generation/crystal_generator.py --list

━━━ Пресеты (готовые соединения) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # UN 3x3x3 (нитрид урана, rock-salt)
  python cris/tools/dataset_generation/crystal_generator.py --preset UN --supercell 3

  # NaCl 5x5x5
  python cris/tools/dataset_generation/crystal_generator.py --preset NaCl --supercell 5

  # UO2 4x4x4 (флюорит)
  python cris/tools/dataset_generation/crystal_generator.py --preset UO2 --supercell 4

  # UC с нестандартным параметром решётки
  python cris/tools/dataset_generation/crystal_generator.py --preset UC --a 4.98 --supercell 3

━━━ Одноатомные структуры (--atom) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # FCC алюминий 5x5x5
  python cris/tools/dataset_generation/crystal_generator.py --lattice cubic_f --atom Al --a 4.046 --supercell 5

  # BCC железо 4x4x4
  python cris/tools/dataset_generation/crystal_generator.py --lattice cubic_i --atom Fe --a 2.866 --supercell 4

  # SC (простая кубическая) 6x6x6
  python cris/tools/dataset_generation/crystal_generator.py --lattice cubic_p --atom Po --a 3.35 --supercell 6

  # HCP цинк (гексагональная), c задаётся отдельно
  python cris/tools/dataset_generation/crystal_generator.py --lattice hex_p --atom Zn --a 2.665 --c 4.947 --supercell 4

  # Тетрагональная структура индия
  python cris/tools/dataset_generation/crystal_generator.py --lattice tetra_i --atom In --a 3.25 --c 4.95 --supercell 4

  # Ромбоэдрическая (тригональная R), задаётся α
  python cris/tools/dataset_generation/crystal_generator.py --lattice trig_r --atom Bi --a 4.75 --alpha 57.3 --supercell 3

  # Орторомбическая, все три параметра разные
  python cris/tools/dataset_generation/crystal_generator.py --lattice ortho_p --atom U --a 2.85 --b 5.87 --c 4.96 --supercell 3

  # Моноклинная, задаётся β
  python cris/tools/dataset_generation/crystal_generator.py --lattice mono_p --atom Se --a 9.05 --b 9.07 --c 11.6 --beta 90.8 --supercell 2

━━━ Многоатомные структуры (--motif) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Формат: --motif SYM fx fy fz  SYM fx fy fz  ...
  Дробные координаты (0..1) в единицах ячейки.

  # Rock-salt вручную (эквивалент --preset NaCl)
  python cris/tools/dataset_generation/crystal_generator.py --lattice cubic_f --a 5.64 \\
      --motif Na 0 0 0  Cl 0.5 0.5 0.5 --supercell 5

  # CsCl-тип (простая кубическая + смещённый второй атом)
  python cris/tools/dataset_generation/crystal_generator.py --lattice cubic_p --a 4.12 \\
      --motif Cs 0 0 0  Cl 0.5 0.5 0.5 --supercell 5

  # Перовскит CaTiO3 (5 атомов в мотиве)
  python cris/tools/dataset_generation/crystal_generator.py --lattice cubic_p --a 3.91 \\
      --motif Ca 0 0 0  Ti 0.5 0.5 0.5  O 0.5 0.5 0  O 0.5 0 0.5  O 0 0.5 0.5 --supercell 3

  # Алмазная структура (FCC + смещение на 0.25 0.25 0.25)
  python cris/tools/dataset_generation/crystal_generator.py --lattice cubic_f --a 3.57 \\
      --motif C 0 0 0  C 0.25 0.25 0.25 --supercell 3

━━━ Шум и вакансии ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # UN с гауссовым шумом 2% от параметра a
  python cris/tools/dataset_generation/crystal_generator.py --preset UN --supercell 3 --noise 2

  # NaCl с 10% вакансий
  python cris/tools/dataset_generation/crystal_generator.py --preset NaCl --supercell 5 --vacancy 0.10

  # UC шум + вакансии одновременно
  python cris/tools/dataset_generation/crystal_generator.py --preset UC --supercell 3 --noise 3 --vacancy 0.05

━━━ Пакетная генерация ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # 50 сэмплов UN (разные seeds, последовательно)
  python cris/tools/dataset_generation/crystal_generator.py --preset UN --supercell 3 --samples 50

  # 200 сэмплов с шумом 2% и вакансиями 10%, 4 процесса параллельно
  python cris/tools/dataset_generation/crystal_generator.py --preset UN --supercell 3 \\
      --noise 2 --vacancy 0.10 --samples 200 --workers 4

  # Фиксированный seed для воспроизводимости
  python cris/tools/dataset_generation/crystal_generator.py --preset NaCl --supercell 5 \\
      --noise 4 --samples 100 --seed 123

━━━ Вывод ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # В конкретную папку с кастомным именем
  python cris/tools/dataset_generation/crystal_generator.py --preset UN --supercell 3 \\
      --out data/structures/macro/source --name UN_3x3x3_clean

  # Асимметричная суперячейка 3x5x3
  python cris/tools/dataset_generation/crystal_generator.py --preset NaCl --supercell 3 5 3
"""

import argparse
import random
import sys
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

try:
    from pymatgen.core import Lattice, Structure
except ImportError:
    print("pymatgen не установлен: pip install pymatgen")
    sys.exit(1)

DEFAULT_OUT = ROOT / "data" / "structures" / "macro" / "source"

# ─── 14 типов решёток Браве ───────────────────────────────────────────────────

LATTICE_TYPES = {
    # Кубическая (a=b=c, α=β=γ=90°)
    "cubic_p":   {"syngony": "cubic",        "centering": "P", "desc": "Кубическая примитивная (SC)"},
    "cubic_i":   {"syngony": "cubic",        "centering": "I", "desc": "Кубическая объёмноцентрированная (BCC)"},
    "cubic_f":   {"syngony": "cubic",        "centering": "F", "desc": "Кубическая гранецентрированная (FCC)"},
    # Тетрагональная (a=b≠c, α=β=γ=90°)
    "tetra_p":   {"syngony": "tetragonal",   "centering": "P", "desc": "Тетрагональная примитивная"},
    "tetra_i":   {"syngony": "tetragonal",   "centering": "I", "desc": "Тетрагональная объёмноцентрированная"},
    # Орторомбическая (a≠b≠c, α=β=γ=90°)
    "ortho_p":   {"syngony": "orthorhombic", "centering": "P", "desc": "Орторомбическая примитивная"},
    "ortho_i":   {"syngony": "orthorhombic", "centering": "I", "desc": "Орторомбическая объёмноцентрированная"},
    "ortho_f":   {"syngony": "orthorhombic", "centering": "F", "desc": "Орторомбическая гранецентрированная"},
    "ortho_c":   {"syngony": "orthorhombic", "centering": "C", "desc": "Орторомбическая базоцентрированная"},
    # Гексагональная / Тригональная
    "hex_p":     {"syngony": "hexagonal",    "centering": "P", "desc": "Гексагональная примитивная"},
    "trig_r":    {"syngony": "trigonal",     "centering": "R", "desc": "Тригональная (ромбоэдрическая)"},
    # Моноклинная (α=γ=90°, β≠90°)
    "mono_p":    {"syngony": "monoclinic",   "centering": "P", "desc": "Моноклинная примитивная"},
    "mono_c":    {"syngony": "monoclinic",   "centering": "C", "desc": "Моноклинная базоцентрированная"},
    # Триклинная
    "triclinic": {"syngony": "triclinic",    "centering": "P", "desc": "Триклинная примитивная"},
}

# Позиции центрирования в дробных координатах ячейки
CENTERING_POSITIONS = {
    "P": [[0.0, 0.0, 0.0]],
    "I": [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
    "F": [[0.0, 0.0, 0.0], [0.5, 0.5, 0.0], [0.5, 0.0, 0.5], [0.0, 0.5, 0.5]],
    "C": [[0.0, 0.0, 0.0], [0.5, 0.5, 0.0]],
    "R": [[0.0, 0.0, 0.0], [2/3, 1/3, 1/3], [1/3, 2/3, 2/3]],
}

# Ограничения сингонии: значение "a" означает скопировать параметр a
SYNGONY_DEFAULTS = {
    "cubic":        {"b": "a", "c": "a", "alpha": 90.0, "beta": 90.0, "gamma": 90.0},
    "tetragonal":   {"b": "a",           "alpha": 90.0, "beta": 90.0, "gamma": 90.0},
    "orthorhombic": {                    "alpha": 90.0, "beta": 90.0, "gamma": 90.0},
    "hexagonal":    {"b": "a",           "alpha": 90.0, "beta": 90.0, "gamma": 120.0},
    "trigonal":     {"b": "a", "c": "a"},
    "monoclinic":   {                    "alpha": 90.0,               "gamma": 90.0},
    "triclinic":    {},
}

# Сгруппированные типы для вывода --list
SYNGONY_GROUPS = {
    "Кубическая":      ["cubic_p", "cubic_i", "cubic_f"],
    "Тетрагональная":  ["tetra_p", "tetra_i"],
    "Орторомбическая": ["ortho_p", "ortho_i", "ortho_f", "ortho_c"],
    "Гексагональная":  ["hex_p"],
    "Тригональная":    ["trig_r"],
    "Моноклинная":     ["mono_p", "mono_c"],
    "Триклинная":      ["triclinic"],
}

# Пресеты популярных соединений: lattice, параметры, мотив
# Мотив: список (symbol, [fx, fy, fz]) — дробные координаты относительно ячейки
COMPOUND_PRESETS = {
    "NaCl": {
        "lattice": "cubic_f", "a": 5.6402,
        "motif": [("Na", [0.0, 0.0, 0.0]), ("Cl", [0.5, 0.5, 0.5])],
        "desc": "Хлорид натрия (rock-salt, Fm-3m)",
    },
    "UN": {
        "lattice": "cubic_f", "a": 4.890,
        "motif": [("U",  [0.0, 0.0, 0.0]), ("N",  [0.5, 0.5, 0.5])],
        "desc": "Нитрид урана (rock-salt, Fm-3m)",
    },
    "UC": {
        "lattice": "cubic_f", "a": 4.960,
        "motif": [("U",  [0.0, 0.0, 0.0]), ("C",  [0.5, 0.5, 0.5])],
        "desc": "Карбид урана (rock-salt, Fm-3m)",
    },
    "UO2": {
        "lattice": "cubic_f", "a": 5.470,
        "motif": [
            ("U", [0.0,  0.0,  0.0 ]),
            ("O", [0.25, 0.25, 0.25]),
            ("O", [0.75, 0.75, 0.25]),
        ],
        "desc": "Диоксид урана (флюорит, Fm-3m)",
    },
    "CsCl": {
        "lattice": "cubic_p", "a": 4.123,
        "motif": [("Cs", [0.0, 0.0, 0.0]), ("Cl", [0.5, 0.5, 0.5])],
        "desc": "Хлорид цезия (Pm-3m)",
    },
    "Al": {
        "lattice": "cubic_f", "a": 4.046,
        "motif": [("Al", [0.0, 0.0, 0.0])],
        "desc": "Алюминий (FCC)",
    },
    "Fe": {
        "lattice": "cubic_i", "a": 2.866,
        "motif": [("Fe", [0.0, 0.0, 0.0])],
        "desc": "Железо α (BCC)",
    },
    "Cu": {
        "lattice": "cubic_f", "a": 3.615,
        "motif": [("Cu", [0.0, 0.0, 0.0])],
        "desc": "Медь (FCC)",
    },
}


# ─── Класс генератора ─────────────────────────────────────────────────────────

class CrystalGenerator:
    """
    Генератор кристаллических структур на основе pymatgen.

    Атрибуты:
        lattice_type  — тип решётки Браве (ключ из LATTICE_TYPES)
        a, b, c       — параметры ячейки (Å)
        alpha, beta, gamma — углы ячейки (°)
    """

    def __init__(self, lattice_type: str, a: float,
                 b: float = None, c: float = None,
                 alpha: float = None, beta: float = None, gamma: float = None):
        if lattice_type not in LATTICE_TYPES:
            raise ValueError(f"Неизвестный тип решётки: '{lattice_type}'. "
                             f"Доступные: {', '.join(LATTICE_TYPES)}")

        info = LATTICE_TYPES[lattice_type]
        self.lattice_type = lattice_type
        self.syngony   = info["syngony"]
        self.centering = info["centering"]

        defs = SYNGONY_DEFAULTS[self.syngony]
        self.a     = a
        self.b     = a if defs.get("b") == "a" else (b or a)
        self.c     = a if defs.get("c") == "a" else (c or a)
        self.alpha = alpha if alpha is not None else defs.get("alpha", 90.0)
        self.beta  = beta  if beta  is not None else defs.get("beta",  90.0)
        self.gamma = gamma if gamma is not None else defs.get("gamma", 90.0)

        self._pmg_lattice = Lattice.from_parameters(
            a=self.a, b=self.b, c=self.c,
            alpha=self.alpha, beta=self.beta, gamma=self.gamma,
        )

    # ── Построение ячейки ─────────────────────────────────────────────────

    def build_unit_cell(self, motif: list) -> Structure:
        """
        Строит элементарную ячейку.

        motif — список (symbol, [fx, fy, fz]).
        Для каждой позиции центрирования размещает полный мотив со смещением.
        """
        centering = CENTERING_POSITIONS[self.centering]
        species, coords = [], []
        for center in centering:
            for symbol, frac in motif:
                pos = [(center[i] + frac[i]) % 1.0 for i in range(3)]
                species.append(symbol)
                coords.append(pos)
        return Structure(self._pmg_lattice, species, coords)

    # ── Генерация суперячейки ─────────────────────────────────────────────

    def generate(self, motif: list,
                 nx: int = 3, ny: int = None, nz: int = None,
                 noise_percent: float = 0.0,
                 vacancy_rate: float = 0.0,
                 seed: int = 42) -> Structure:
        """
        Генерирует суперячейку nx×ny×nz с опциональным шумом и вакансиями.
        Возвращает pymatgen Structure.
        """
        ny = ny or nx
        nz = nz or nx

        structure = self.build_unit_cell(motif)
        structure.make_supercell([nx, ny, nz])

        if noise_percent > 0.0:
            structure = _apply_noise(structure, noise_percent, seed)
        if vacancy_rate > 0.0:
            structure = _apply_vacancies(structure, vacancy_rate, seed)

        return structure

    def params_summary(self) -> str:
        return (f"a={self.a} b={self.b} c={self.c} "
                f"α={self.alpha} β={self.beta} γ={self.gamma}")


# ─── Вспомогательные функции ──────────────────────────────────────────────────

def _apply_noise(structure: Structure, noise_percent: float, seed: int) -> Structure:
    """Гауссовый шум к декартовым координатам. σ = noise_percent/100 × a."""
    rng = np.random.default_rng(seed)
    sigma = noise_percent / 100.0 * structure.lattice.a
    new_species, new_coords = [], []
    for site in structure:
        new_species.append(site.specie.symbol)
        new_coords.append(site.coords + rng.normal(0.0, sigma, 3))
    return Structure(structure.lattice, new_species, new_coords, coords_are_cartesian=True)


def _apply_vacancies(structure: Structure, rate: float, seed: int) -> Structure:
    """Случайно удаляет rate долю атомов. Оставляет ≥1 атом каждого вида."""
    rng = random.Random(seed)
    sites = list(structure)
    n_remove = max(1, int(len(sites) * rate))
    indices = list(range(len(sites)))
    rng.shuffle(indices)
    remove = set(indices[:n_remove])

    remaining = [s for i, s in enumerate(sites) if i not in remove]

    # Восстанавливаем полностью пропавшие типы
    remaining_types = {s.specie.symbol for s in remaining}
    for atype in {s.specie.symbol for s in sites} - remaining_types:
        remaining.append(next(s for s in sites if s.specie.symbol == atype))

    return Structure.from_sites(remaining)


def _save_xyz(structure: Structure, filepath: Path, comment: str = ""):
    """Сохраняет структуру в XYZ-формате."""
    lines = [str(len(structure)), comment or structure.formula]
    for site in structure:
        x, y, z = site.coords
        lines.append(f" {site.specie.symbol}    {x:.6f}    {y:.6f}    {z:.6f}")
    filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_comment(gen: CrystalGenerator, motif: list, sc: tuple,
                   noise_percent: float, vacancy_rate: float) -> str:
    formula = "".join(f"{s}{'' if motif.count((s, None)) == 1 else ''}" for s, _ in motif)
    parts = [
        LATTICE_TYPES[gen.lattice_type]["desc"],
        gen.params_summary(),
        f"supercell={'x'.join(map(str, sc))}",
    ]
    if noise_percent > 0:
        parts.append(f"noise={noise_percent}%")
    if vacancy_rate > 0:
        parts.append(f"vacancy={int(vacancy_rate * 100)}%")
    return " | ".join(parts)


# ─── Параллельная генерация ───────────────────────────────────────────────────

def _generate_one(args):
    """Воркер для multiprocessing.Pool."""
    (lattice_type, lattice_params, motif, nx, ny, nz,
     noise_percent, vacancy_rate, seed, filepath, comment) = args

    gen = CrystalGenerator(lattice_type, **lattice_params)
    s = gen.generate(motif, nx, ny, nz, noise_percent, vacancy_rate, seed)
    _save_xyz(s, Path(filepath), comment)
    return filepath, len(s)


def generate_samples(gen: CrystalGenerator, motif: list,
                     nx: int, ny: int, nz: int,
                     noise_percent: float, vacancy_rate: float,
                     samples: int, out_dir: Path,
                     name_base: str, seed: int = 42,
                     workers: int = 1):
    """
    Генерирует samples файлов. При workers > 1 — параллельно.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    sc = (nx, ny, nz)
    comment = _build_comment(gen, motif, sc, noise_percent, vacancy_rate)

    lattice_params = {
        "a": gen.a, "b": gen.b, "c": gen.c,
        "alpha": gen.alpha, "beta": gen.beta, "gamma": gen.gamma,
    }

    tasks = []
    for i in range(1, samples + 1):
        if samples == 1:
            fname = f"{name_base}.xyz"
        else:
            fname = f"{name_base}_s{i:03d}.xyz"
        tasks.append((
            gen.lattice_type, lattice_params, motif,
            nx, ny, nz, noise_percent, vacancy_rate,
            seed + i, str(out_dir / fname), comment,
        ))

    w = min(workers, samples, cpu_count())
    if w > 1:
        with Pool(processes=w) as pool:
            results = pool.map(_generate_one, tasks)
    else:
        results = [_generate_one(t) for t in tasks]

    for filepath, n_atoms in results:
        print(f"  {Path(filepath).name}  ({n_atoms} атомов)")


def _show_info():
    print("\n  14 типов решёток Браве:\n")
    for group, types in SYNGONY_GROUPS.items():
        print(f"  {group}:")
        for lt in types:
            info = LATTICE_TYPES[lt]
            n = len(CENTERING_POSITIONS[info["centering"]])
            print(f"    {lt:12}  {n} позиции   {info['desc']}")
    print()
    print("  Пресеты соединений:")
    for k, v in COMPOUND_PRESETS.items():
        natoms = len(v["motif"])
        n_per_cell = natoms * len(CENTERING_POSITIONS[LATTICE_TYPES[v["lattice"]]["centering"]])
        print(f"    {k:8}  a={v['a']:.3f} Å  {n_per_cell} атомов/ячейка  {v['desc']}")
    print()


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Генератор кристаллических структур (14 типов Браве, pymatgen)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""примеры:
  python cris/tools/dataset_generation/crystal_generator.py --list
  python cris/tools/dataset_generation/crystal_generator.py --preset UN --supercell 3
  python cris/tools/dataset_generation/crystal_generator.py --lattice cubic_f --atom Al --a 4.046 --supercell 5
  python cris/tools/dataset_generation/crystal_generator.py --lattice cubic_f --a 5.64 --motif Na 0 0 0 Cl 0.5 0.5 0.5 --supercell 5
  python cris/tools/dataset_generation/crystal_generator.py --preset UN --supercell 3 --noise 2 --vacancy 0.10 --samples 20 --workers 4
""",
    )

    parser.add_argument("--list", action="store_true", help="Список типов решёток и пресетов")

    # Структура
    parser.add_argument("--preset",  type=str, help=f"Пресет соединения: {', '.join(COMPOUND_PRESETS)}")
    parser.add_argument("--lattice", type=str, help=f"Тип решётки: {', '.join(LATTICE_TYPES)}")
    parser.add_argument("--atom",    type=str, default=None, help="Атом для одноатомного режима")
    parser.add_argument("--motif",   type=str, nargs="+", default=None,
                        metavar="SYM_FX_FY_FZ",
                        help="Мотив: Na 0 0 0 Cl 0.5 0.5 0.5  (символ + 3 дробные координаты, повторить для каждого атома)")

    # Параметры решётки
    parser.add_argument("--a",     type=float, default=None)
    parser.add_argument("--b",     type=float, default=None)
    parser.add_argument("--c",     type=float, default=None)
    parser.add_argument("--alpha", type=float, default=None)
    parser.add_argument("--beta",  type=float, default=None)
    parser.add_argument("--gamma", type=float, default=None)

    # Суперячейка и эффекты
    parser.add_argument("--supercell", "-n", type=int, nargs="+", default=[3], metavar="N",
                        help="Размер суперячейки: 5 → 5x5x5 или 3 5 3 → 3x5x3")
    parser.add_argument("--noise",    type=float, default=0.0, help="Шум, %% от a (например 2.0)")
    parser.add_argument("--vacancy",  type=float, default=0.0, help="Доля вакансий 0..1 (например 0.10)")
    parser.add_argument("--samples",  type=int,   default=1,   help="Количество файлов (по умолчанию 1)")
    parser.add_argument("--workers",  type=int,   default=1,   help="Параллельных процессов")
    parser.add_argument("--seed",     type=int,   default=42,  help="Random seed")

    # Вывод
    parser.add_argument("--out",  type=Path, default=None,
                        help="Папка вывода (по умолчанию data/structures/macro/source/)")
    parser.add_argument("--name", type=str, default=None, help="Базовое имя файла (без .xyz)")

    args = parser.parse_args()
    out_dir = args.out or DEFAULT_OUT

    # ── --list ───────────────────────────────────────────────────────────
    if args.list:
        _show_info()
        return

    if not args.preset and not args.lattice:
        parser.print_help()
        return

    # ── Разбор аргументов ────────────────────────────────────────────────

    # Разбираем пресет или параметры вручную
    if args.preset:
        if args.preset not in COMPOUND_PRESETS:
            print(f"Неизвестный пресет: '{args.preset}'. Доступные: {', '.join(COMPOUND_PRESETS)}")
            sys.exit(1)
        preset = COMPOUND_PRESETS[args.preset]
        lattice_type = preset["lattice"]
        motif        = preset["motif"]
        lp = {"a": args.a or preset["a"]}
        name_base = args.name or args.preset
    else:
        if args.lattice not in LATTICE_TYPES:
            print(f"Неизвестный тип решётки: '{args.lattice}'. Доступные: {', '.join(LATTICE_TYPES)}")
            sys.exit(1)
        lattice_type = args.lattice
        lp = {k: getattr(args, k) for k in ("a", "b", "c", "alpha", "beta", "gamma")
              if getattr(args, k) is not None}
        if not lp.get("a"):
            print("Укажите параметр --a")
            sys.exit(1)

        # Мотив
        if args.motif:
            tokens = args.motif
            if len(tokens) % 4 != 0:
                print("--motif: ожидается кратное 4 количество токенов: SYM FX FY FZ ...")
                sys.exit(1)
            motif = []
            for i in range(0, len(tokens), 4):
                sym = tokens[i]
                frac = [float(tokens[i+1]), float(tokens[i+2]), float(tokens[i+3])]
                motif.append((sym, frac))
        elif args.atom:
            motif = [(args.atom, [0.0, 0.0, 0.0])]
        else:
            print("Укажите --atom <символ> или --motif SYM FX FY FZ ...")
            sys.exit(1)

        atom_str  = "_".join(s for s, _ in motif)
        name_base = args.name or f"{lattice_type}_{atom_str}"

    # Суперячейка
    sc = args.supercell
    if len(sc) == 1:
        sc = [sc[0], sc[0], sc[0]]
    elif len(sc) != 3:
        print("--supercell: 1 или 3 значения")
        sys.exit(1)

    gen = CrystalGenerator(lattice_type, **lp)
    sc_str = "x".join(map(str, sc))

    # Формируем тэги для имени файла
    tags = [name_base, sc_str]
    if args.noise > 0:
        tags.append(f"noise{args.noise}pct")
    if args.vacancy > 0:
        tags.append(f"vac{int(args.vacancy * 100)}pct")
    name_base_full = "_".join(tags)

    print(f"\nРешётка  : {lattice_type} — {LATTICE_TYPES[lattice_type]['desc']}")
    print(f"Параметры: {gen.params_summary()}")
    print(f"Мотив    : {', '.join(f'{s} {f}' for s, f in motif)}")
    print(f"Ячейка   : {len(gen.build_unit_cell(motif))} атомов × {sc_str} = ~{len(gen.build_unit_cell(motif)) * sc[0]*sc[1]*sc[2]} атомов")
    print(f"Вывод    : {out_dir}\n")

    generate_samples(
        gen, motif, sc[0], sc[1], sc[2],
        args.noise, args.vacancy,
        samples=args.samples,
        out_dir=out_dir,
        name_base=name_base_full if args.samples > 1 else (args.name or name_base),
        seed=args.seed,
        workers=args.workers,
    )


if __name__ == "__main__":
    main()
