"""
Основная логика поиска эталонных структур по нормализованным координатам.
Координаты читаются напрямую из XYZ-файлов — таблица structure_site не используется.
"""
from collections import Counter
from pathlib import Path

from cris.db.connection import get_cursor
from cris.core.coordinates import shift_coordinates, normalize_coordinates
from cris.logger import logger

_ROOT = Path(__file__).parent.parent.parent   # корень проекта
_COORD_TOLERANCE = 1e-4                        # допуск при сравнении координат


# ── Вспомогательные функции ───────────────────────────────────────────────────

def _parse_xyz(xyz_path: Path) -> list[list]:
    """Парсит XYZ-файл → [[symbol, x, y, z], ...]."""
    lines = xyz_path.read_text(encoding="utf-8").splitlines()
    atom_count = int(lines[0].strip())
    result = []
    for line in lines[2:2 + atom_count]:
        parts = line.split()
        if len(parts) >= 4:
            result.append([parts[0], float(parts[1]), float(parts[2]), float(parts[3])])
    return result


def _normalize_xyz(xyz_path: Path) -> list[list] | None:
    """Загружает XYZ-файл и возвращает нормализованные координаты [[sym, nx, ny, nz], ...]."""
    try:
        data = _parse_xyz(xyz_path)
        shifted = shift_coordinates(data)
        return normalize_coordinates(shifted)
    except Exception as e:
        logger.warning("_normalize_xyz: failed for {}: {}", xyz_path, e)
        return None


# ── Основная функция поиска ───────────────────────────────────────────────────

def check_coords(coordinates: dict, ion_amount: int):
    """
    Ищет эталонные структуры по нормализованным координатам.

    coordinates : dict {n: [label, norm_x, norm_y, norm_z]}  — уже нормализованные
    ion_amount  : ожидаемое число ионов в эталонной структуре

    Алгоритм:
      1. Загружаем все reference_structure с xyz_path из БД
      2. Для каждой структуры читаем XYZ, нормализуем, фильтруем по числу атомов
      3. Для каждой входной координаты ищем совпадение в эталоне (± tolerance)
         Каждое совпадение — один голос за эту структуру
      4. Строим вероятности по числу голосов

    Возвращает [[lattice_names, struct_names], [top_lattice_info, prob], [top_struct_info, prob]]
    или False если совпадений не найдено.
    """
    # 1. Загружаем все структуры с xyz_path
    try:
        with get_cursor() as cur:
            cur.execute("""
                SELECT rs.id, rs.lattice_type_id, rs.xyz_path
                FROM reference_structure rs
                WHERE rs.xyz_path IS NOT NULL AND rs.xyz_path != ''
            """)
            structures = cur.fetchall()
    except Exception as e:
        logger.error("check_coords: failed to load structures from DB: {}", e)
        return False

    if not structures:
        logger.warning("check_coords: no reference structures with xyz_path found")
        return False

    # Нормализованные входные координаты (x, y, z)
    input_coords = [(float(v[1]), float(v[2]), float(v[3])) for v in coordinates.values()]

    matched_lattices   = []
    matched_structures = []

    for struct_id, lt_id, xyz_rel_path in structures:
        xyz_path = _ROOT / xyz_rel_path
        if not xyz_path.exists():
            logger.warning("check_coords: XYZ not found for struct_id={}: {}", struct_id, xyz_path)
            continue

        normalized = _normalize_xyz(xyz_path)
        if normalized is None:
            continue

        if len(normalized) != ion_amount:
            continue

        ref_coords = [(float(r[1]), float(r[2]), float(r[3])) for r in normalized]

        # Для каждой входной координаты считаем один голос, если нашлось совпадение
        for ix, iy, iz in input_coords:
            for rx, ry, rz in ref_coords:
                if (abs(ix - rx) <= _COORD_TOLERANCE and
                        abs(iy - ry) <= _COORD_TOLERANCE and
                        abs(iz - rz) <= _COORD_TOLERANCE):
                    matched_lattices.append(lt_id)
                    matched_structures.append(struct_id)
                    break  # один голос за структуру на одну входную координату

    if not matched_lattices:
        return False

    # 2. Считаем вероятности
    lattice_counts = Counter(matched_lattices)
    lattice_total  = sum(lattice_counts.values())
    lattice_probs  = {k: v / lattice_total * 100 for k, v in lattice_counts.items()}

    struct_counts  = Counter(matched_structures)
    struct_total   = sum(struct_counts.values())
    struct_probs   = {k: v / struct_total * 100 for k, v in struct_counts.items()}

    top_lt_id   = max(lattice_probs, key=lattice_probs.get)
    top_lt_prob = lattice_probs[top_lt_id]
    top_st_id   = max(struct_probs,  key=struct_probs.get)
    top_st_prob = struct_probs[top_st_id]

    # 3. Собираем детальную информацию из БД
    lattice_names  = []
    struct_names   = []
    lattice_info   = None
    structure_info = None

    try:
        with get_cursor() as cur:
            for lt_id in set(matched_lattices):
                cur.execute(
                    "SELECT id, name_en, name_ru, description FROM lattice_type WHERE id = %s",
                    (lt_id,)
                )
                row = cur.fetchone()
                if row:
                    lattice_names.append([row[0], row[2], row[1], lattice_probs[lt_id]])
                    if lt_id == top_lt_id:
                        lattice_info = row

            for st_id in set(matched_structures):
                cur.execute("""
                    SELECT id, name, cell_length_a, cell_length_b, cell_length_c,
                           cell_volume, cell_angle_alpha, cell_angle_beta, cell_angle_gamma,
                           sg_number, sg_hall, sg_hm, doi, formula
                    FROM reference_structure WHERE id = %s
                """, (st_id,))
                row = cur.fetchone()
                if row:
                    struct_names.append([row[0], row[1], struct_probs[st_id]])
                    if st_id == top_st_id:
                        structure_info = row
    except Exception as e:
        logger.error("check_coords (fetch info) failed: {}", e)

    return [
        [lattice_names, struct_names],
        [lattice_info, top_lt_prob],
        [structure_info, top_st_prob],
    ]
