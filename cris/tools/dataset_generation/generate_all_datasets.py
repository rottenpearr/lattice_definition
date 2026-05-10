"""
Генерирует KDE-датасеты для всех XYZ-структур в data/structures/.

Проходит по micro/source, micro/generated, macro/source, macro/generated
и запускает generate_dataset() для каждого файла.

Поддерживает resume: пропускает структуры у которых уже достаточно итераций.

Использование:
    # Все структуры (дефолт: 400 сэмплов, шум 4%)
    python ML/CatBoost/generate_all_datasets.py

    # Только micro/source, 1000 сэмплов
    python ML/CatBoost/generate_all_datasets.py --source micro/source --samples 1000

    # Несколько уровней шума
    python ML/CatBoost/generate_all_datasets.py --noise 2 4 8

    # Пересчитать даже если датасет уже есть
    python ML/CatBoost/generate_all_datasets.py --force
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from cris.tools.generate_dataset import generate_dataset
STRUCTURES_DIR = ROOT / "data" / "structures"
DATASETS_DIR   = ROOT / "data" / "kde_arrays"

# Все подпапки структур и соответствующие папки датасетов
STRUCTURE_SOURCES = [
    ("micro/source",     "micro/source"),
    ("micro/generated",  "micro/generated"),
    ("macro/source",     "macro/source"),
    ("macro/generated",  "macro/generated"),
]


def count_existing_samples(dataset_path: Path) -> int:
    """Считает сколько итераций уже сгенерировано (по подпапкам 1, 2, 3...)."""
    if not dataset_path.exists():
        return 0
    return sum(1 for d in dataset_path.iterdir() if d.is_dir() and d.name.isdigit())


def generate_for_file(xyz_path: Path, out_dir: Path, substance_name: str,
                      samples: int, noise: float, force: bool):
    dataset_path = out_dir / substance_name
    existing = count_existing_samples(dataset_path)

    if not force and existing >= samples:
        print(f"    Пропуск (уже {existing}/{samples} итераций): {substance_name}")
        return False

    start_from = 0 if force else existing
    remaining = samples - start_from

    if start_from > 0:
        print(f"    Resume с итерации {start_from + 1} (осталось {remaining}): {substance_name}")
    else:
        print(f"    Генерация {samples} сэмплов: {substance_name}")

    # substance_id — первая часть имени файла до '_'
    substance_id = xyz_path.stem.split("_")[0]

    generate_dataset(
        xyz_filepath=str(xyz_path),
        substance_id=substance_id,
        substance_name=substance_name,
        total_samples=samples,
        noise_percent=noise,
        out_dir=str(out_dir),
    )
    return True


def main(sources: list = None, samples: int = 400, noise_levels: list = None, force: bool = False):
    noise_levels = noise_levels or [4]
    active_sources = sources or [s[0] for s in STRUCTURE_SOURCES]

    total_files = 0
    total_generated = 0

    for src_rel, dst_rel in STRUCTURE_SOURCES:
        if src_rel not in active_sources:
            continue

        src_dir = STRUCTURES_DIR / Path(src_rel)
        if not src_dir.exists():
            print(f"Папка не найдена, пропуск: {src_dir}")
            continue

        xyz_files = sorted(src_dir.glob("*.xyz"))
        if not xyz_files:
            print(f"Нет XYZ-файлов в {src_dir}")
            continue

        print(f"\n{'='*55}")
        print(f"  {src_rel}  ({len(xyz_files)} файлов)")
        print(f"{'='*55}")

        for xyz_path in xyz_files:
            total_files += 1
            for noise in noise_levels:
                # Имя датасета: stem + суффикс шума если уровней несколько
                if len(noise_levels) > 1:
                    substance_name = f"{xyz_path.stem}_noise{noise}pct"
                else:
                    substance_name = xyz_path.stem

                out_dir = DATASETS_DIR / dst_rel
                out_dir.mkdir(parents=True, exist_ok=True)

                try:
                    generated = generate_for_file(
                        xyz_path, out_dir, substance_name,
                        samples=samples, noise=noise, force=force
                    )
                    if generated:
                        total_generated += 1
                except Exception as e:
                    print(f"    ОШИБКА {xyz_path.name} (шум {noise}%): {e}")

    print(f"\n{'='*55}")
    print(f"Готово: обработано файлов {total_files}, сгенерировано датасетов {total_generated}")
    print(f"Датасеты в: {DATASETS_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Генерация KDE-датасетов для всех структур")
    parser.add_argument(
        "--source", nargs="+", default=None,
        choices=["micro/source", "micro/generated", "macro/source", "macro/generated"],
        help="Папки для обработки (по умолчанию все)"
    )
    parser.add_argument("--samples", type=int, default=400,
                        help="Количество сэмплов на структуру (по умолчанию 400)")
    parser.add_argument("--noise", type=float, nargs="+", default=[4],
                        help="Уровни шума в %% (по умолчанию 4). Можно несколько: --noise 2 4 8")
    parser.add_argument("--force", action="store_true",
                        help="Пересчитать даже если датасет уже существует")
    args = parser.parse_args()

    main(sources=args.source, samples=args.samples, noise_levels=args.noise, force=args.force)
