"""
Генерирует структуры с вакансиями из XYZ-файлов и сохраняет в data/structures/inaccurate/.

Для каждого исходного файла создаёт несколько вариантов с разным процентом вакансий.
Вакансии расставляются случайно, с фиксированным seed для воспроизводимости.

Использование:
    # Обработать все структуры из accurate/
    python ML/CatBoost/generate_vacancies.py

    # Только конкретный файл
    python ML/CatBoost/generate_vacancies.py --input data/structures/accurate/UC.xyz

    # Задать уровни вакансий и количество вариантов
    python ML/CatBoost/generate_vacancies.py --rates 0.05 0.10 0.15 --variants 3
"""

import argparse
import random
from pathlib import Path

# Пути по умолчанию
ACCURATE_DIR = Path(__file__).parent.parent.parent / "data" / "structures" / "accurate"
INACCURATE_DIR = Path(__file__).parent.parent.parent / "data" / "structures" / "inaccurate"

# Уровни вакансий по умолчанию (доля удалённых атомов)
DEFAULT_RATES = [0.05, 0.10, 0.15]

# Количество случайных вариантов на каждый уровень вакансий
DEFAULT_VARIANTS = 3


def parse_xyz(filepath: Path):
    """Читает XYZ-файл. Возвращает (comment, atoms) где atoms = [['U', x, y, z], ...]."""
    lines = filepath.read_text().splitlines()
    atom_count = int(lines[0].strip())
    comment = lines[1].strip()
    atoms = []
    for line in lines[2:2 + atom_count]:
        parts = line.split()
        atoms.append([parts[0], float(parts[1]), float(parts[2]), float(parts[3])])
    return comment, atoms


def write_xyz(filepath: Path, atoms: list, comment: str = ""):
    """Записывает список атомов в XYZ-файл."""
    lines = [str(len(atoms)), comment]
    for atom in atoms:
        lines.append(f" {atom[0]}    {atom[1]:.6f}    {atom[2]:.6f}    {atom[3]:.6f}")
    filepath.write_text("\n".join(lines) + "\n")


def generate_vacancies(atoms: list, vacancy_rate: float, seed: int) -> list:
    """
    Случайно удаляет vacancy_rate долю атомов.
    Гарантирует что хотя бы 1 атом каждого типа остаётся.
    """
    rng = random.Random(seed)
    n_remove = max(1, int(len(atoms) * vacancy_rate))

    # Перемешиваем индексы и удаляем первые n_remove
    indices = list(range(len(atoms)))
    rng.shuffle(indices)
    remove_set = set(indices[:n_remove])

    result = [atom for i, atom in enumerate(atoms) if i not in remove_set]

    # Проверяем что не удалили все атомы одного типа
    remaining_types = {atom[0] for atom in result}
    original_types = {atom[0] for atom in atoms}
    if remaining_types != original_types:
        # Восстанавливаем по одному атому каждого потерянного типа
        for atom_type in original_types - remaining_types:
            candidate = next(a for a in atoms if a[0] == atom_type)
            result.append(candidate)

    return result


def process_file(xyz_path: Path, rates: list, variants: int, out_dir: Path):
    """Генерирует inaccurate-версии одного XYZ-файла."""
    try:
        comment, atoms = parse_xyz(xyz_path)
    except Exception as e:
        print(f"  Ошибка чтения {xyz_path.name}: {e}")
        return 0

    stem = xyz_path.stem  # например "UC" или "UC_mp-2489"
    generated = 0

    for rate in rates:
        rate_pct = int(rate * 100)
        for variant in range(1, variants + 1):
            seed = hash((stem, rate, variant)) % (2 ** 31)
            result_atoms = generate_vacancies(atoms, rate, seed)

            n_removed = len(atoms) - len(result_atoms)
            out_name = f"{stem}-vacancy{rate_pct}pct_v{variant}.xyz"
            out_path = out_dir / out_name

            if out_path.exists():
                print(f"    Уже есть: {out_name}")
                continue

            new_comment = f"{comment} | vacancy={rate_pct}% removed={n_removed} variant={variant}"
            write_xyz(out_path, result_atoms, new_comment)
            print(f"    {out_name}  ({len(atoms)} → {len(result_atoms)} атомов, -{n_removed})")
            generated += 1

    return generated


def main(input_path: Path = None, rates: list = None, variants: int = None):
    rates = rates or DEFAULT_RATES
    variants = variants or DEFAULT_VARIANTS
    INACCURATE_DIR.mkdir(parents=True, exist_ok=True)

    if input_path:
        files = [input_path]
    else:
        files = sorted(ACCURATE_DIR.glob("*.xyz"))

    if not files:
        print(f"Не найдено XYZ-файлов в {ACCURATE_DIR}")
        return

    total = 0
    print(f"Уровни вакансий: {[f'{int(r*100)}%' for r in rates]}, вариантов на уровень: {variants}")
    print(f"Выходная папка: {INACCURATE_DIR}\n")

    for xyz_path in files:
        print(f"  {xyz_path.name}")
        count = process_file(xyz_path, rates, variants, INACCURATE_DIR)
        total += count

    print(f"\nГотово: сгенерировано {total} файлов.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Генерация структур с вакансиями из XYZ")
    parser.add_argument("--input", type=Path, default=None, help="Конкретный XYZ-файл (по умолчанию все из accurate/)")
    parser.add_argument("--rates", type=float, nargs="+", default=DEFAULT_RATES, help="Уровни вакансий (доли, например 0.05 0.10 0.15)")
    parser.add_argument("--variants", type=int, default=DEFAULT_VARIANTS, help="Вариантов на уровень вакансий")
    args = parser.parse_args()

    main(input_path=args.input, rates=args.rates, variants=args.variants)
