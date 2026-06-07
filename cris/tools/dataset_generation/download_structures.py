"""
Скачивает структуры из Materials Project API, сохраняет XYZ-файлы
и заносит метаданные в таблицу reference_structure.

Использует pymatgen для раскрытия симметрии: каждая структура сохраняется
как полная конвенциональная ячейка (все эквивалентные позиции заполнены),
а не только асимметричная единица.

API-ключ читается из .env файла (MP_API_KEY=...) или передаётся через --api-key.

Использование:
    python -m cris.tools.dataset_generation.download_structures
    python -m cris.tools.dataset_generation.download_structures --limit 50
    python -m cris.tools.dataset_generation.download_structures --formula UC
    python -m cris.tools.dataset_generation.download_structures --dry-run
    python -m cris.tools.dataset_generation.download_structures --cif path/to/file.cif

Зависимости:
    pip install mp-api pymatgen python-dotenv psycopg2-binary
"""

import argparse
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_ROOT))

import psycopg2
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from cris.db.config import db_config

# ── Пути ─────────────────────────────────────────────────────────────────────
OUT_DIR = _ROOT / "data" / "structures" / "micro" / "source"

# Элементы для поиска (по умолчанию)
SEARCH_ELEMENTS = ["U"]

# ── Маппинг crystal_system → name_en в таблице lattice_type ──────────────────
_CRYSTAL_SYSTEM_MAP = {
    "cubic":        "cubic",
    "hexagonal":    "hexagonal",
    "tetragonal":   "tetragonal",
    "orthorhombic": "orthorhombic",
    "trigonal":     "trigonal",
    "monoclinic":   "monoclinic",
    "triclinic":    "triclinic",
}


# ── Вспомогательные функции ───────────────────────────────────────────────────

def load_api_key(cli_key: str = None) -> str:
    """Читает API-ключ из аргумента CLI, затем из .env, затем из переменной окружения."""
    if cli_key:
        return cli_key
    env_path = _ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("MP_API_KEY=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    key = os.environ.get("MP_API_KEY")
    if key:
        return key
    raise ValueError(
        "API-ключ не найден. Добавьте MP_API_KEY=<ключ> в .env "
        "или передайте через --api-key."
    )


def _expand_to_conventional(structure):
    """
    Раскрывает структуру до полной конвенциональной ячейки через SpacegroupAnalyzer.

    MP API иногда возвращает примитивную ячейку (меньше атомов).
    После этого вызова все позиции, эквивалентные по симметрии, заполнены.
    Это то, что VESTA показывает при открытии CIF-файла.
    """
    try:
        sga = SpacegroupAnalyzer(structure)
        return sga.get_conventional_standard_structure()
    except Exception as e:
        print(f"  WARN: не удалось раскрыть симметрию ({e}), используем исходную структуру")
        return structure


def _site_symbol(site) -> str:
    """Возвращает символ элемента для сайта (поддерживает упорядоченные и неупорядоченные сайты)."""
    if site.is_ordered:
        return site.specie.symbol
    # Для неупорядоченных сайтов берём наиболее вероятный элемент
    return max(site.species, key=lambda sp: site.species[sp]).symbol


def structure_to_xyz(structure, filepath: Path, comment: str = "") -> int:
    """
    Записывает pymatgen Structure в XYZ-файл.

    Ожидает уже раскрытую (конвенциональную) структуру.
    Возвращает количество записанных атомов.
    """
    sites = structure.sites
    lines = [
        str(len(sites)),
        comment or structure.formula,
    ]
    for site in sites:
        coords = site.coords  # Декартовы координаты в Å
        symbol = _site_symbol(site)
        lines.append(f" {symbol}    {coords[0]:.6f}    {coords[1]:.6f}    {coords[2]:.6f}")
    filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(sites)


def cif_to_xyz(cif_path: Path, xyz_path: Path, comment: str = "") -> int:
    """
    Конвертирует CIF-файл в XYZ с полным раскрытием симметрии через pymatgen.

    Читает CIF, применяет операции симметрии пространственной группы,
    записывает полную конвенциональную ячейку в XYZ.
    Возвращает количество атомов.
    """
    from pymatgen.io.cif import CifParser
    parser = CifParser(str(cif_path))
    # primitive=False → конвенциональная ячейка, occupancy_tolerance → для частичных заселённостей
    structures = parser.parse_structures(primitive=False, occupancy_tolerance=2.0)
    if not structures:
        raise ValueError(f"Не удалось прочитать структуры из {cif_path}")
    structure = structures[0]
    xyz_path.parent.mkdir(parents=True, exist_ok=True)
    n = structure_to_xyz(structure, xyz_path, comment or cif_path.stem)
    return n


def _get_lattice_type_id(cur, crystal_system: str) -> int | None:
    """Ищет lattice_type_id по crystal_system из MP API."""
    name_en = _CRYSTAL_SYSTEM_MAP.get((crystal_system or "").lower())
    if not name_en:
        return None
    cur.execute(
        "SELECT id FROM lattice_type WHERE LOWER(name_en) = LOWER(%s) LIMIT 1",
        (name_en,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def _upsert_structure(cur, *, mp_id: str, name: str, formula: str,
                      lattice_type_id: int | None,
                      cell_a: float, cell_b: float, cell_c: float,
                      cell_vol: float,
                      angle_alpha: float, angle_beta: float, angle_gamma: float,
                      sg_number: int | None, sg_hm: str | None,
                      xyz_path_rel: str,
                      source_url: str) -> tuple[int, bool]:
    """
    Вставляет новую запись или обновляет существующую по mp_id.
    Возвращает (structure_id, created: bool).
    """
    cur.execute("SELECT id FROM reference_structure WHERE mp_id = %s", (mp_id,))
    existing = cur.fetchone()

    if existing:
        struct_id = existing[0]
        cur.execute("""
            UPDATE reference_structure SET
                name             = %s,
                formula          = %s,
                lattice_type_id  = COALESCE(%s, lattice_type_id),
                cell_length_a    = %s,
                cell_length_b    = %s,
                cell_length_c    = %s,
                cell_volume      = %s,
                cell_angle_alpha = %s,
                cell_angle_beta  = %s,
                cell_angle_gamma = %s,
                sg_number        = %s,
                sg_hm            = %s,
                xyz_path         = %s,
                source_url       = %s
            WHERE id = %s
        """, (name, formula, lattice_type_id,
              cell_a, cell_b, cell_c, cell_vol,
              angle_alpha, angle_beta, angle_gamma,
              sg_number, sg_hm,
              xyz_path_rel, source_url,
              struct_id))
        return struct_id, False
    else:
        lt_id = lattice_type_id
        if lt_id is None:
            cur.execute("SELECT id FROM lattice_type ORDER BY id LIMIT 1")
            row = cur.fetchone()
            lt_id = row[0] if row else 1

        cur.execute("""
            INSERT INTO reference_structure
                (name, formula, lattice_type_id,
                 cell_length_a, cell_length_b, cell_length_c, cell_volume,
                 cell_angle_alpha, cell_angle_beta, cell_angle_gamma,
                 sg_number, sg_hm,
                 mp_id, xyz_path, source_url,
                 existence_status)
            VALUES
                (%s, %s, %s,
                 %s, %s, %s, %s,
                 %s, %s, %s,
                 %s, %s,
                 %s, %s, %s,
                 'experimental')
            RETURNING id
        """, (name, formula, lt_id,
              cell_a, cell_b, cell_c, cell_vol,
              angle_alpha, angle_beta, angle_gamma,
              sg_number, sg_hm,
              mp_id, xyz_path_rel, source_url))
        struct_id = cur.fetchone()[0]
        return struct_id, True


# ── Основная функция ──────────────────────────────────────────────────────────

def download_structures(api_key: str, limit: int = 50,
                        formula: str = None, dry_run: bool = False) -> None:
    from mp_api.client import MPRester

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Подключение к Materials Project API...")
    with MPRester(api_key=api_key) as mpr:
        search_kwargs = dict(
            # "structure" не запрашиваем здесь — получим отдельно как conventional
            fields=["material_id", "formula_pretty", "symmetry"],
            deprecated=False,
        )
        if formula:
            search_kwargs["formula"] = formula
        else:
            search_kwargs["elements"] = SEARCH_ELEMENTS

        print(f"Поиск структур (лимит: {limit})...")
        docs = mpr.materials.search(**search_kwargs)
        # Ограничиваем сразу — docs может быть большим
        docs = list(docs)[:limit]

        print(f"Найдено: {len(docs)}. Скачиваем конвенциональные ячейки...")
        structures = {}
        for doc in docs:
            mp_id = str(doc.material_id)
            try:
                # conventional_unit_cell=True — гарантированно полная ячейка
                # со всеми позициями, эквивалентными по симметрии
                structures[mp_id] = mpr.get_structure_by_material_id(
                    mp_id, conventional_unit_cell=True
                )
            except Exception as e:
                print(f"  WARN: не удалось скачать структуру {mp_id}: {e}")
                structures[mp_id] = None

    saved = updated = skipped = 0

    conn = psycopg2.connect(**db_config) if not dry_run else None
    cur  = conn.cursor() if conn else None

    try:
        for doc in docs:
            mp_id          = str(doc.material_id)
            formula_pretty = doc.formula_pretty
            sym            = doc.symmetry

            conv_structure = structures.get(mp_id)
            if conv_structure is None:
                print(f"  Пропуск {mp_id}: структура недоступна")
                skipped += 1
                continue

            n_atoms = len(conv_structure.sites)
            print(f"  {formula_pretty} ({mp_id}): {n_atoms} атомов")

            # ── Параметры ячейки ──────────────────────────────────────────
            lat      = conv_structure.lattice
            cell_a   = float(lat.a)
            cell_b   = float(lat.b)
            cell_c   = float(lat.c)
            cell_vol = float(lat.volume)
            alpha    = float(lat.alpha)
            beta     = float(lat.beta)
            gamma    = float(lat.gamma)

            sg_hm     = sym.symbol     if sym else None
            sg_number = int(sym.number) if sym and sym.number else None
            cs        = sym.crystal_system.value if sym and hasattr(sym.crystal_system, "value") \
                        else (str(sym.crystal_system) if sym else None)

            safe_formula = formula_pretty.replace(" ", "")
            filename     = f"{safe_formula}_{mp_id}.xyz"
            filepath     = OUT_DIR / filename
            xyz_path_rel = str(filepath.relative_to(_ROOT)).replace("\\", "/")
            source_url   = f"https://materialsproject.org/materials/{mp_id}"
            comment      = f"{formula_pretty} {mp_id} sg={sg_hm or 'unknown'}"

            # ── XYZ-файл ─────────────────────────────────────────────────
            if filepath.exists():
                print(f"  XYZ уже есть: {filename}")
            elif not dry_run:
                try:
                    n = structure_to_xyz(conv_structure, filepath, comment)
                    print(f"  XYZ сохранён: {filename}  ({n} атомов, sg={sg_hm})")
                except Exception as e:
                    print(f"  Ошибка записи XYZ {mp_id}: {e}")
                    skipped += 1
                    continue
            else:
                print(f"  [DRY RUN] XYZ: {filename}  ({n_atoms} атомов, sg={sg_hm})")

            # ── БД ────────────────────────────────────────────────────────
            if dry_run:
                lt_name = _CRYSTAL_SYSTEM_MAP.get((cs or "").lower(), "?")
                print(f"  [DRY RUN] DB: mp_id={mp_id}  formula={formula_pretty}"
                      f"  lattice={lt_name}  sg={sg_hm}  a={cell_a:.4f}")
                saved += 1
                continue

            try:
                lt_id = _get_lattice_type_id(cur, cs)
                if lt_id is None:
                    print(f"  WARN: crystal_system='{cs}' не найден в lattice_type для {mp_id}")

                struct_id, created = _upsert_structure(
                    cur,
                    mp_id           = mp_id,
                    name            = formula_pretty,
                    formula         = formula_pretty,
                    lattice_type_id = lt_id,
                    cell_a          = cell_a,
                    cell_b          = cell_b,
                    cell_c          = cell_c,
                    cell_vol        = cell_vol,
                    angle_alpha     = alpha,
                    angle_beta      = beta,
                    angle_gamma     = gamma,
                    sg_number       = sg_number,
                    sg_hm           = sg_hm,
                    xyz_path_rel    = xyz_path_rel,
                    source_url      = source_url,
                )
                conn.commit()

                action = "INSERT" if created else "UPDATE"
                print(f"  DB {action}: id={struct_id}  {formula_pretty}  ({mp_id})")
                if created:
                    saved += 1
                else:
                    updated += 1

            except Exception as e:
                conn.rollback()
                print(f"  Ошибка БД {mp_id}: {e}")
                skipped += 1

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    status = "[DRY RUN] " if dry_run else ""
    print(f"\n{status}Готово: вставлено={saved}, обновлено={updated}, пропущено={skipped}.")
    print(f"Папка XYZ: {OUT_DIR}")


def download_by_ids(api_key: str, mp_ids: list[str], dry_run: bool = False) -> None:
    """Скачивает конкретные структуры по списку MP ID."""
    from mp_api.client import MPRester

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    saved = updated = skipped = 0

    conn = psycopg2.connect(**db_config) if not dry_run else None
    cur  = conn.cursor() if conn else None

    try:
        with MPRester(api_key=api_key) as mpr:
            for mp_id in mp_ids:
                mp_id = mp_id.strip()
                print(f"\nСкачиваю {mp_id}...")
                try:
                    structure = mpr.get_structure_by_material_id(mp_id, conventional_unit_cell=True)
                except Exception as e:
                    print(f"  Ошибка: {e}"); skipped += 1; continue

                # Метаданные симметрии
                try:
                    docs = mpr.materials.search(
                        material_ids=[mp_id],
                        fields=["formula_pretty", "symmetry"],
                    )
                    doc = docs[0] if docs else None
                except Exception:
                    doc = None

                formula_pretty = doc.formula_pretty if doc else structure.formula
                sym            = doc.symmetry       if doc else None
                sg_hm     = sym.symbol      if sym else None
                sg_number = int(sym.number) if sym and sym.number else None
                cs        = sym.crystal_system.value if sym and hasattr(sym.crystal_system, "value") \
                            else (str(sym.crystal_system) if sym else None)

                lat      = structure.lattice
                cell_a, cell_b, cell_c = float(lat.a), float(lat.b), float(lat.c)
                cell_vol = float(lat.volume)
                alpha, beta, gamma = float(lat.alpha), float(lat.beta), float(lat.gamma)
                n_atoms  = len(structure.sites)

                safe_formula = formula_pretty.replace(" ", "")
                filename     = f"{safe_formula}_{mp_id}.xyz"
                filepath     = OUT_DIR / filename
                xyz_path_rel = str(filepath.relative_to(_ROOT)).replace("\\", "/")
                source_url   = f"https://materialsproject.org/materials/{mp_id}"
                comment      = f"{formula_pretty} {mp_id} sg={sg_hm or 'unknown'}"

                print(f"  {formula_pretty}  {n_atoms} атомов  sg={sg_hm}")

                if filepath.exists():
                    print(f"  XYZ уже есть: {filename}")
                elif not dry_run:
                    structure_to_xyz(structure, filepath, comment)
                    print(f"  XYZ сохранён: {filename}")
                else:
                    print(f"  [DRY RUN] XYZ: {filename}")

                if dry_run:
                    saved += 1; continue

                try:
                    lt_id = _get_lattice_type_id(cur, cs)
                    struct_id, created = _upsert_structure(
                        cur, mp_id=mp_id, name=formula_pretty, formula=formula_pretty,
                        lattice_type_id=lt_id,
                        cell_a=cell_a, cell_b=cell_b, cell_c=cell_c, cell_vol=cell_vol,
                        angle_alpha=alpha, angle_beta=beta, angle_gamma=gamma,
                        sg_number=sg_number, sg_hm=sg_hm,
                        xyz_path_rel=xyz_path_rel, source_url=source_url,
                    )
                    conn.commit()
                    action = "INSERT" if created else "UPDATE"
                    print(f"  DB {action}: id={struct_id}")
                    saved += 1 if created else 0
                    updated += 0 if created else 1
                except Exception as e:
                    conn.rollback(); print(f"  Ошибка БД: {e}"); skipped += 1
    finally:
        if cur:  cur.close()
        if conn: conn.close()

    print(f"\nГотово: вставлено={saved}, обновлено={updated}, пропущено={skipped}.")


def convert_cif(cif_path: Path, out_dir: Path = None) -> None:
    """Конвертирует один CIF-файл в XYZ с раскрытием симметрии."""
    out_dir = out_dir or OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    xyz_path = out_dir / (cif_path.stem + ".xyz")
    print(f"Конвертация: {cif_path.name} → {xyz_path.name}")
    n = cif_to_xyz(cif_path, xyz_path)
    print(f"  Записано {n} атомов → {xyz_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Скачать структуры из Materials Project / конвертировать CIF")
    parser.add_argument("--api-key", default=None, help="MP API ключ (или MP_API_KEY в .env)")
    parser.add_argument("--limit",   type=int, default=50, help="Максимум структур (по умолчанию 50)")
    parser.add_argument("--formula", type=str, default=None, help="Фильтр по формуле, например 'UC'")
    parser.add_argument("--mp-id",   type=str, nargs="+", default=None,
                        help="Один или несколько MP ID, например --mp-id mp-1568 mp-2489")
    parser.add_argument("--dry-run", action="store_true", help="Показать план без записи в БД/файлы")
    parser.add_argument("--cif",     type=str, default=None, help="Путь к CIF-файлу для локальной конвертации")
    args = parser.parse_args()

    if args.cif:
        convert_cif(Path(args.cif))
    elif args.mp_id:
        key = load_api_key(args.api_key)
        download_by_ids(key, args.mp_id, dry_run=args.dry_run)
    else:
        key = load_api_key(args.api_key)
        download_structures(
            api_key = key,
            limit   = args.limit,
            formula = args.formula,
            dry_run = args.dry_run,
        )
