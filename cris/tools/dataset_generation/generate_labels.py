"""
Генерирует data/kde_arrays/labels.csv — маппинг имя структуры → тип решётки.

Алгоритм:
  1. Сканирует data/structures/ (micro/source, macro/source, micro/generated, macro/generated)
  2. Source-структуры с mp_id/cod_id → запрос в БД (reference_structure → lattice_type)
  3. Синтетические macro без DB → тип решётки из имени файла (cubic_f_Al → cubic_f)
  4. Generated-структуры → наследуют метку от source
  5. Сохраняет labels.csv (перезаписывает)

CSV-формат:
    name,lattice_type
    UC_mp-72,cubic_f
    UC_mp-72_vac5pct_001,cubic_f
    cubic_f_Al,cubic_f

Запуск:
    python cris/tools/dataset_generation/generate_labels.py
    python cris/tools/dataset_generation/generate_labels.py --out data/kde_arrays/labels.csv
    python cris/tools/dataset_generation/generate_labels.py --no-db  # только синтетические
"""

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from cris.tools.dataset_generation.naming import (
    is_generated, get_source_stem, lattice_type_from_stem
)

DEFAULT_OUT = ROOT / "data" / "kde_arrays" / "labels.csv"

STRUCTURES_DIR = ROOT / "data" / "structures"
SCAN_DIRS = [
    STRUCTURES_DIR / "micro" / "source",
    STRUCTURES_DIR / "micro" / "generated",
    STRUCTURES_DIR / "macro" / "source",
    STRUCTURES_DIR / "macro" / "generated",
]


# ─── Поиск метки через БД ────────────────────────────────────────────────────

def _db_labels() -> dict[str, str]:
    """
    Возвращает {stem: lattice_type_name} для всех записей в reference_structure.
    Ключ — stem XYZ-файла (поле xyz_path или mp_id/cod_id в имени).
    """
    try:
        from cris.db.connection import get_cursor
    except ImportError:
        return {}

    labels = {}
    try:
        with get_cursor() as cur:
            cur.execute("""
                SELECT rs.mp_id, rs.cod_id, rs.xyz_path, lt.name_en
                FROM reference_structure rs
                JOIN lattice_type lt ON lt.id = rs.lattice_type_id
            """)
            for mp_id, cod_id, xyz_path, lt_name in cur.fetchall():
                # Ключ по mp_id
                if mp_id:
                    labels[mp_id] = lt_name
                # Ключ по cod_id
                if cod_id:
                    labels[f"cod-{cod_id}"] = lt_name
                # Ключ по stem из xyz_path
                if xyz_path:
                    labels[Path(xyz_path).stem] = lt_name
    except Exception as e:
        print(f"  [DB] Не удалось получить метки: {e}")

    return labels


def _label_for_stem(stem: str, db: dict[str, str]) -> str | None:
    """
    Определяет lattice_type для одного stem.
    Порядок приоритетов:
      1. DB lookup по stem напрямую
      2. DB lookup по mp_id/cod_id внутри имени (UC_mp-72 → mp-72)
      3. Извлечение из имени (cubic_f_Al → cubic_f)
    """
    source = get_source_stem(stem)

    # 1. Прямой поиск по stem
    if source in db:
        return db[source]

    # 2. Поиск по ID внутри имени: берём часть после первого '_' если там 'mp-' или 'cod-'
    parts = source.split('_')
    for part in parts:
        if part.startswith('mp-') or part.startswith('cod-'):
            if part in db:
                return db[part]

    # 3. Из имени файла (синтетические macro)
    return lattice_type_from_stem(source)


# ─── Основная логика ─────────────────────────────────────────────────────────

def generate_labels(out_path: Path = DEFAULT_OUT, use_db: bool = True,
                    verbose: bool = True) -> dict[str, str]:
    """
    Сканирует data/structures/, собирает метки, сохраняет labels.csv.
    Возвращает словарь {stem: lattice_type}.
    """
    db = _db_labels() if use_db else {}
    if verbose and db:
        print(f"  [DB] Загружено меток из БД: {len(db)}")
    elif verbose and use_db:
        print("  [DB] БД недоступна или пуста — используются только имена файлов")

    labels: dict[str, str] = {}
    skipped: list[str] = []

    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for xyz_path in sorted(scan_dir.glob("*.xyz")):
            stem = xyz_path.stem
            lt = _label_for_stem(stem, db)
            if lt:
                labels[stem] = lt
            else:
                skipped.append(stem)

    # Также добавляем структуры из kde_arrays/ которых ещё нет
    kde_dir = ROOT / "data" / "kde_arrays"
    for subdir in ["micro", "macro"]:
        for struct_dir in sorted((kde_dir / subdir).glob("*")):
            if struct_dir.is_dir() and struct_dir.name not in labels:
                lt = _label_for_stem(struct_dir.name, db)
                if lt:
                    labels[struct_dir.name] = lt
                else:
                    skipped.append(struct_dir.name)

    # Сохраняем
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "lattice_type"])
        for name, lt in sorted(labels.items()):
            writer.writerow([name, lt])

    if verbose:
        print(f"\nСохранено меток: {len(labels)}  →  {out_path}")
        if skipped:
            print(f"Без метки (пропущено): {len(skipped)}")
            for s in skipped[:10]:
                print(f"  {s}")
            if len(skipped) > 10:
                print(f"  ... и ещё {len(skipped) - 10}")

    return labels


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Генерация labels.csv для ML-обучения")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help=f"Путь к выходному файлу (по умолчанию {DEFAULT_OUT})")
    parser.add_argument("--no-db", action="store_true",
                        help="Не обращаться к БД, только имена файлов")
    args = parser.parse_args()

    print(f"Генерация меток...\n")
    result = generate_labels(out_path=args.out, use_db=not args.no_db)
    print(f"\nРаспределение по типам решёток:")
    from collections import Counter
    for lt, cnt in sorted(Counter(result.values()).items()):
        print(f"  {lt:15s}  {cnt}")
