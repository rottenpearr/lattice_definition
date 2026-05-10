"""
Генерирует XYZ-структуры кристаллических решёток через pymatgen.

Поддерживает 12 предустановленных структур (все основные типы Браве).
Каждый пресет задаёт решётку (Lattice) и мотив — список атомов с дробными
координатами внутри ячейки. Параметры решётки и виды атомов можно переопределить
через CLI.

Использование:
    # Список доступных структур
    python cris/tools/dataset_generation/generate_structures.py --list

    # NaCl 5x5x5
    python cris/tools/dataset_generation/generate_structures.py --structure nacl --supercell 5

    # UN 3x3x3 с вакансиями 10%
    python cris/tools/dataset_generation/generate_structures.py --structure un --supercell 3 --vacancy 0.10

    # UO2 3x3x3 с шумом 2% и вакансиями 5%, 20 сэмплов
    python cris/tools/dataset_generation/generate_structures.py --structure uo2 --supercell 3 --noise 2 --vacancy 0.05 --samples 20

    # FCC с кастомным атомом и параметром решётки
    python cris/tools/dataset_generation/generate_structures.py --structure fcc --species Al Al Al Al --a 4.05 --supercell 4

    # Асимметричная суперячейка 3x5x3
    python cris/tools/dataset_generation/generate_structures.py --structure nacl --supercell 3 5 3

    # Сохранить в конкретную папку
    python cris/tools/dataset_generation/generate_structures.py --structure un --supercell 5 --out data/structures/micro/source
"""

import argparse
import random
import sys
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

# ─── Предустановленные структуры ──────────────────────────────────────────────
# params: параметры решётки (a, b, c, alpha, beta, gamma).
#   Если b/c не указаны — берётся a. Если углы не указаны — 90°.
# species: виды атомов мотива (можно переопределить через --species).
# coords: дробные координаты атомов мотива в ячейке.

PRESETS = {
    # ── Кубические ──────────────────────────────────────────────────────────
    "sc": {
        "desc": "Простая кубическая (SC, Pm-3m)",
        "params": {"a": 3.0},
        "species": ["X"],
        "coords": [[0.0, 0.0, 0.0]],
    },
    "bcc": {
        "desc": "Объёмноцентрированная кубическая (BCC, Im-3m)",
        "params": {"a": 3.3},
        "species": ["X", "X"],
        "coords": [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
    },
    "fcc": {
        "desc": "Гранецентрированная кубическая (FCC, Fm-3m)",
        "params": {"a": 4.05},
        "species": ["X", "X", "X", "X"],
        "coords": [
            [0.0, 0.0, 0.0], [0.5, 0.5, 0.0],
            [0.5, 0.0, 0.5], [0.0, 0.5, 0.5],
        ],
    },
    "nacl": {
        "desc": "Rock-salt NaCl (Fm-3m), a=5.64 Å — 8 атомов в ячейке",
        "params": {"a": 5.6402},
        "species": ["Na", "Cl", "Na", "Cl", "Na", "Cl", "Na", "Cl"],
        "coords": [
            [0.0, 0.0, 0.0], [0.5, 0.5, 0.5],
            [0.5, 0.5, 0.0], [0.0, 0.0, 0.5],
            [0.5, 0.0, 0.5], [0.0, 0.5, 0.0],
            [0.0, 0.5, 0.5], [0.5, 0.0, 0.0],
        ],
    },
    "un": {
        "desc": "Нитрид урана UN (rock-salt, Fm-3m), a=4.89 Å",
        "params": {"a": 4.890},
        "species": ["U", "N", "U", "N", "U", "N", "U", "N"],
        "coords": [
            [0.0, 0.0, 0.0], [0.5, 0.5, 0.5],
            [0.5, 0.5, 0.0], [0.0, 0.0, 0.5],
            [0.5, 0.0, 0.5], [0.0, 0.5, 0.0],
            [0.0, 0.5, 0.5], [0.5, 0.0, 0.0],
        ],
    },
    "uc": {
        "desc": "Карбид урана UC (rock-salt, Fm-3m), a=4.96 Å",
        "params": {"a": 4.960},
        "species": ["U", "C", "U", "C", "U", "C", "U", "C"],
        "coords": [
            [0.0, 0.0, 0.0], [0.5, 0.5, 0.5],
            [0.5, 0.5, 0.0], [0.0, 0.0, 0.5],
            [0.5, 0.0, 0.5], [0.0, 0.5, 0.0],
            [0.0, 0.5, 0.5], [0.5, 0.0, 0.0],
        ],
    },
    "uo2": {
        "desc": "Диоксид урана UO2 (флюорит, Fm-3m), a=5.47 Å — 12 атомов",
        "params": {"a": 5.470},
        "species": ["U", "U", "U", "U", "O", "O", "O", "O", "O", "O", "O", "O"],
        "coords": [
            # U — FCC-позиции
            [0.0, 0.0, 0.0], [0.5, 0.5, 0.0],
            [0.5, 0.0, 0.5], [0.0, 0.5, 0.5],
            # O — тетраэдрические пустоты
            [0.25, 0.25, 0.25], [0.75, 0.75, 0.25],
            [0.75, 0.25, 0.75], [0.25, 0.75, 0.75],
            [0.75, 0.75, 0.75], [0.25, 0.25, 0.75],
            [0.25, 0.75, 0.25], [0.75, 0.25, 0.25],
        ],
    },
    "cscl": {
        "desc": "Цезий-хлоридная CsCl (Pm-3m), a=4.12 Å — 2 атома",
        "params": {"a": 4.123},
        "species": ["Cs", "Cl"],
        "coords": [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
    },
    "perovskite": {
        "desc": "Перовскит ABO3 (CaTiO3, Pm-3m), a=3.91 Å — 5 атомов",
        "params": {"a": 3.905},
        "species": ["Ca", "Ti", "O", "O", "O"],
        "coords": [
            [0.0, 0.0, 0.0],  # A — угол
            [0.5, 0.5, 0.5],  # B — центр
            [0.5, 0.5, 0.0],  # O — грани
            [0.5, 0.0, 0.5],
            [0.0, 0.5, 0.5],
        ],
    },
    "diamond": {
        "desc": "Алмазная кубическая (Fd-3m), a=3.57 Å — 8 атомов",
        "params": {"a": 3.567},
        "species": ["C"] * 8,
        "coords": [
            [0.0, 0.0, 0.0], [0.5, 0.5, 0.0],
            [0.5, 0.0, 0.5], [0.0, 0.5, 0.5],
            [0.25, 0.25, 0.25], [0.75, 0.75, 0.25],
            [0.75, 0.25, 0.75], [0.25, 0.75, 0.75],
        ],
    },
    # ── Гексагональные ──────────────────────────────────────────────────────
    "hcp": {
        "desc": "Гексагональная плотноупакованная (HCP, P6_3/mmc), a=3.21 Å c=5.21 Å",
        "params": {"a": 3.21, "c": 5.21, "alpha": 90, "beta": 90, "gamma": 120},
        "species": ["X", "X"],
        "coords": [
            [0.0, 0.0, 0.0],
            [1/3, 2/3, 0.5],
        ],
    },
    "wurtzite": {
        "desc": "Вюрцит ZnS (P6_3mc), a=3.82 Å c=6.26 Å — 4 атома",
        "params": {"a": 3.820, "c": 6.260, "alpha": 90, "beta": 90, "gamma": 120},
        "species": ["Zn", "Zn", "S", "S"],
        "coords": [
            [1/3, 2/3, 0.0],
            [2/3, 1/3, 0.5],
            [1/3, 2/3, 0.375],
            [2/3, 1/3, 0.875],
        ],
    },
}


# ─── Вспомогательные функции ──────────────────────────────────────────────────

def build_lattice(params: dict) -> Lattice:
    a = params.get("a", 4.0)
    b = params.get("b", a)
    c = params.get("c", a)
    alpha = params.get("alpha", 90.0)
    beta  = params.get("beta",  90.0)
    gamma = params.get("gamma", 90.0)
    return Lattice.from_parameters(a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)


def apply_noise(structure: Structure, noise_percent: float, seed: int) -> Structure:
    """Гауссовый шум к декартовым координатам. Сигма = noise_percent/100 * a."""
    rng = np.random.default_rng(seed)
    sigma = noise_percent / 100.0 * structure.lattice.a
    new_species, new_coords = [], []
    for site in structure:
        displacement = rng.normal(0.0, sigma, 3)
        new_species.append(site.specie.symbol)
        new_coords.append(site.coords + displacement)
    return Structure(structure.lattice, new_species, new_coords, coords_are_cartesian=True)


def apply_vacancies(structure: Structure, rate: float, seed: int) -> Structure:
    """Случайно удаляет rate долю атомов. Гарантирует >= 1 атом каждого вида."""
    rng = random.Random(seed)
    sites = list(structure)
    n_remove = max(1, int(len(sites) * rate))
    indices = list(range(len(sites)))
    rng.shuffle(indices)
    remove = set(indices[:n_remove])

    remaining = [s for i, s in enumerate(sites) if i not in remove]

    # Восстанавливаем пропавшие типы
    remaining_types = {s.specie.symbol for s in remaining}
    for atype in {s.specie.symbol for s in sites} - remaining_types:
        remaining.append(next(s for s in sites if s.specie.symbol == atype))

    return Structure.from_sites(remaining)


def structure_to_xyz(structure: Structure, filepath: Path, comment: str = ""):
    """Сохраняет структуру в XYZ-формате, совместимом с пайплайном CRIS."""
    lines = [str(len(structure)), comment or structure.formula]
    for site in structure:
        x, y, z = site.coords
        lines.append(f" {site.specie.symbol}    {x:.6f}    {y:.6f}    {z:.6f}")
    filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ─── Основная логика ──────────────────────────────────────────────────────────

def generate(
    preset_name: str,
    supercell: list,
    out_dir: Path,
    name: str = None,
    species_override: list = None,
    lattice_override: dict = None,
    noise_percent: float = 0.0,
    vacancy_rate: float = 0.0,
    samples: int = 1,
    seed: int = 42,
):
    preset = PRESETS[preset_name]

    params = dict(preset["params"])
    if lattice_override:
        params.update({k: v for k, v in lattice_override.items() if v is not None})

    lattice = build_lattice(params)
    species = species_override if species_override else preset["species"]
    coords  = preset["coords"]

    if len(species) != len(coords):
        raise ValueError(
            f"--species задаёт {len(species)} атомов, "
            f"а пресет '{preset_name}' ожидает {len(coords)}"
        )

    base = Structure(lattice, species, coords)
    base.make_supercell(supercell)

    out_dir.mkdir(parents=True, exist_ok=True)
    sc_str = "x".join(map(str, supercell))

    for i in range(1, samples + 1):
        s = base.copy()
        tag_parts = [preset_name, sc_str]

        if noise_percent > 0:
            s = apply_noise(s, noise_percent, seed=seed + i)
            tag_parts.append(f"noise{noise_percent}pct")

        if vacancy_rate > 0:
            s = apply_vacancies(s, vacancy_rate, seed=seed + i * 1000)
            tag_parts.append(f"vac{int(vacancy_rate * 100)}pct")

        if samples > 1:
            tag_parts.append(f"s{i:03d}")

        if name:
            fname = f"{name}.xyz" if samples == 1 else f"{name}_s{i:03d}.xyz"
        else:
            fname = "_".join(tag_parts) + ".xyz"

        comment_parts = [
            s.formula,
            preset["desc"],
            f"supercell={sc_str}",
        ]
        if noise_percent > 0:
            comment_parts.append(f"noise={noise_percent}%")
        if vacancy_rate > 0:
            comment_parts.append(f"vacancy={int(vacancy_rate * 100)}%")

        structure_to_xyz(s, out_dir / fname, " | ".join(comment_parts))

        status = f"[{i}/{samples}] " if samples > 1 else ""
        print(f"  {status}{fname}  ({len(s)} атомов)")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Генерация XYZ-структур кристаллических решёток через pymatgen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""примеры:
  python cris/tools/dataset_generation/generate_structures.py --list
  python cris/tools/dataset_generation/generate_structures.py --structure nacl --supercell 5
  python cris/tools/dataset_generation/generate_structures.py --structure un --supercell 3 --vacancy 0.10
  python cris/tools/dataset_generation/generate_structures.py --structure uo2 --supercell 3 --noise 2 --vacancy 0.05 --samples 20
  python cris/tools/dataset_generation/generate_structures.py --structure fcc --species Al Al Al Al --a 4.05 --supercell 4
  python cris/tools/dataset_generation/generate_structures.py --structure nacl --supercell 3 5 3
""",
    )

    parser.add_argument("--list", action="store_true",
                        help="Показать список доступных структур")
    parser.add_argument("--structure", "-s", type=str,
                        help="Тип структуры (nacl, un, uc, fcc, ...)")
    parser.add_argument("--supercell", "-n", type=int, nargs="+", default=[1], metavar="N",
                        help="Размер суперячейки: 5 → 5x5x5, или 3 5 3 → 3x5x3")
    parser.add_argument("--species", type=str, nargs="+", default=None,
                        help="Переопределить виды атомов (количество = количеству атомов в пресете)")
    parser.add_argument("--a",     type=float, default=None, help="Параметр решётки a (Å)")
    parser.add_argument("--b",     type=float, default=None, help="Параметр решётки b (Å)")
    parser.add_argument("--c",     type=float, default=None, help="Параметр решётки c (Å)")
    parser.add_argument("--alpha", type=float, default=None, help="Угол α (°)")
    parser.add_argument("--beta",  type=float, default=None, help="Угол β (°)")
    parser.add_argument("--gamma", type=float, default=None, help="Угол γ (°)")
    parser.add_argument("--noise", type=float, default=0.0,
                        help="Гауссовый шум, %% от параметра решётки a (например 2.0)")
    parser.add_argument("--vacancy", type=float, default=0.0,
                        help="Доля удалённых атомов (0.05 = 5%%)")
    parser.add_argument("--samples", type=int, default=1,
                        help="Количество генерируемых файлов (для датасета)")
    parser.add_argument("--out", type=Path, default=None,
                        help=f"Папка вывода (по умолчанию data/structures/macro/source/)")
    parser.add_argument("--name", type=str, default=None,
                        help="Базовое имя файла (без .xyz). При samples>1 добавляется _s001, _s002...")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (по умолчанию 42)")

    args = parser.parse_args()

    if args.list:
        print("\nДоступные структуры:\n")
        for key, val in PRESETS.items():
            n = len(val["coords"])
            print(f"  {key:<14} {n:>2} атома/ов   {val['desc']}")
        print()
        return

    if not args.structure:
        parser.print_help()
        return

    if args.structure not in PRESETS:
        print(f"Неизвестная структура: '{args.structure}'")
        print(f"Доступные: {', '.join(PRESETS)}")
        sys.exit(1)

    sc = args.supercell
    if len(sc) == 1:
        sc = [sc[0], sc[0], sc[0]]
    elif len(sc) != 3:
        print("--supercell принимает 1 значение (N → NxNxN) или 3 (NX NY NZ)")
        sys.exit(1)

    lattice_override = {
        k: getattr(args, k)
        for k in ("a", "b", "c", "alpha", "beta", "gamma")
        if getattr(args, k) is not None
    }

    out_dir = args.out or DEFAULT_OUT

    print(f"\nСтруктура : {args.structure} — {PRESETS[args.structure]['desc']}")
    print(f"Суперячейка: {'x'.join(map(str, sc))}")
    print(f"Вывод      : {out_dir}\n")

    generate(
        preset_name=args.structure,
        supercell=sc,
        out_dir=out_dir,
        name=args.name,
        species_override=args.species,
        lattice_override=lattice_override or None,
        noise_percent=args.noise,
        vacancy_rate=args.vacancy,
        samples=args.samples,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
