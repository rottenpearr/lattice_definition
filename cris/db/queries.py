"""
Основная логика поиска эталонных структур по нормализованным координатам.
Координаты читаются напрямую из XYZ-файлов — таблица structure_site не используется.

Два метода поиска:
  check_coords()     — точное сравнение координат (работает только при совпадении числа атомов)
  check_coords_kde() — косинусное сходство KDE-векторов (инвариантно к суперячейкам,
                       сдвигам, поворотам; используется как fallback)
"""
from collections import Counter
from pathlib import Path

import numpy as np

from cris.db.connection import get_cursor
from cris.core.coordinates import shift_coordinates, normalize_coordinates
from cris.logger import logger

_ROOT            = Path(__file__).parent.parent.parent   # корень проекта
_COORD_TOLERANCE = 1e-4                                   # допуск при сравнении координат
_KDE_THRESHOLD   = 0.80                                   # минимальное косинусное сходство


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


# ── Вспомогательный запрос: детали структуры и типа решётки ─────────────────

def _fetch_struct_info(struct_id: int, lt_id: int, struct_prob: float, lt_prob: float):
    """
    Возвращает [[lattice_names, struct_names], [lattice_info, lt_prob], [struct_info, st_prob]]
    — тот же формат что и check_coords.
    """
    lattice_info   = None
    structure_info = None
    lattice_names  = []
    struct_names   = []

    try:
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, name_en, name_ru, description FROM lattice_type WHERE id = %s",
                (lt_id,)
            )
            row = cur.fetchone()
            if row:
                lattice_info = row
                lattice_names.append([row[0], row[2], row[1], lt_prob])

            cur.execute("""
                SELECT id, name, cell_length_a, cell_length_b, cell_length_c,
                       cell_volume, cell_angle_alpha, cell_angle_beta, cell_angle_gamma,
                       sg_number, sg_hall, sg_hm, doi, formula
                FROM reference_structure WHERE id = %s
            """, (struct_id,))
            row = cur.fetchone()
            if row:
                structure_info = row
                struct_names.append([row[0], row[1], struct_prob])
    except Exception as e:
        logger.error("_fetch_struct_info failed: {}", e)

    return [
        [lattice_names, struct_names],
        [lattice_info,   lt_prob],
        [structure_info, struct_prob],
    ]


# ── KDE-поиск: косинусное сходство векторов распределения расстояний ─────────

def check_coords_kde(normalized_coords: list, top_k: int = 1):
    """
    Ищет эталонную структуру по сходству KDE-векторов (200-dim).

    Преимущества перед check_coords:
      - Работает с суперячейками (вектор инвариантен к числу атомов)
      - Устойчив к сдвигу и небольшому повороту
      - Не требует точного числа атомов

    Порог сходства: _KDE_THRESHOLD (по умолчанию 0.80).
    Возвращает тот же формат что и check_coords, или False если ничего не найдено.
    """
    from cris.core.ml_predict import _coords_to_feature_vector_200

    # KDE-вектор входной структуры
    input_vec = _coords_to_feature_vector_200(normalized_coords)
    if input_vec is None:
        logger.warning("check_coords_kde: failed to compute KDE vector for input")
        return False

    norm_input = np.linalg.norm(input_vec)
    if norm_input == 0:
        return False

    # Загружаем все эталоны с xyz_path
    try:
        with get_cursor() as cur:
            cur.execute("""
                SELECT rs.id, rs.lattice_type_id, rs.xyz_path
                FROM reference_structure rs
                WHERE rs.xyz_path IS NOT NULL AND rs.xyz_path != ''
            """)
            structures = cur.fetchall()
    except Exception as e:
        logger.error("check_coords_kde: DB load failed: {}", e)
        return False

    if not structures:
        return False

    # Считаем косинусное сходство для каждого эталона
    scores = []
    for struct_id, lt_id, xyz_rel_path in structures:
        xyz_path = _ROOT / xyz_rel_path
        normalized_ref = _normalize_xyz(xyz_path)
        if normalized_ref is None:
            continue

        ref_vec = _coords_to_feature_vector_200(normalized_ref)
        if ref_vec is None:
            continue

        norm_ref = np.linalg.norm(ref_vec)
        if norm_ref == 0:
            continue

        similarity = float(np.dot(input_vec, ref_vec) / (norm_input * norm_ref))
        scores.append((struct_id, lt_id, similarity))

    if not scores:
        return False

    scores.sort(key=lambda x: x[2], reverse=True)
    best_struct_id, best_lt_id, best_sim = scores[0]

    logger.debug("check_coords_kde: best match struct_id={} sim={:.3f}", best_struct_id, best_sim)

    if best_sim < _KDE_THRESHOLD:
        logger.debug("check_coords_kde: best similarity {:.3f} below threshold {}", best_sim, _KDE_THRESHOLD)
        return False

    return _fetch_struct_info(best_struct_id, best_lt_id,
                              struct_prob=round(best_sim * 100, 1),
                              lt_prob=round(best_sim * 100, 1))


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

        # Разрешаем суперячейки: входных атомов должно быть кратно числу атомов эталона
        if ion_amount % len(normalized) != 0:
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
        logger.debug("check_coords: no exact match, falling back to KDE search")
        coord_list = list(coordinates.values())
        return check_coords_kde(coord_list)

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
