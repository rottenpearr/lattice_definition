import os
from collections import Counter
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import gaussian_kde

from cris.db.connection import get_cursor
from cris.core.coordinates import shift_coordinates, normalize_coordinates
from cris.core.vectors import get_lattice_vectors2

_ROOT = Path(__file__).parent.parent.parent  # корень проекта


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


def create_all_spectrum_plots():
    """
    Строит спектры для всех эталонных структур в БД.
    Координаты читаются из XYZ-файлов (reference_structure.xyz_path).
    """
    try:
        with get_cursor() as cur:
            cur.execute("""
                SELECT id, xyz_path FROM reference_structure
                WHERE xyz_path IS NOT NULL AND xyz_path != ''
                ORDER BY id
            """)
            rows = cur.fetchall()
    except Exception as e:
        print(f"Произошла ошибка при чтении БД: {e}")
        return

    for struct_id, xyz_rel_path in rows:
        xyz_path = _ROOT / xyz_rel_path
        if not xyz_path.exists():
            print(f"XYZ не найден для structure_id={struct_id}: {xyz_path}")
            continue

        try:
            data = _parse_xyz(xyz_path)
        except Exception as e:
            print(f"Ошибка парсинга {xyz_path}: {e}")
            continue

        shifted    = shift_coordinates(data)
        normalized = normalize_coordinates(shifted)

        # Преобразуем в формат, ожидаемый get_lattice_vectors2: {n: (id, x, y, z)}
        data_dict = {}
        for i, row in enumerate(normalized):
            data_dict[i + 1] = (struct_id, row[1], row[2], row[3])

        vectors = get_lattice_vectors2(normalized)
        for vec_id, ion in enumerate(vectors.keys()):
            ion_coords = [float(elem) for elem in ion.split(";")]
            plot_spectra(
                data=dict(Counter(vectors[ion])),
                ion=ion_coords,
                substance_id=struct_id,
                vector_id=vec_id,
                cmap="plasma",
                background="#20232a",
            )


def plot_spectra(data, ion, substance_id, vector_id, cmap="plasma", background="#1e1e1e", outdir="../../data/spectrum"):
    """
    Строит спектры (гистограммы) для набора расстояний между ионами.

    data : dict
        Словарь {расстояние: частота}
    cmap : str
        Цветовая схема для градиента
    background : str
        Цвет фона графиков
    """
    outdir += f"/spectrum_{str(substance_id)}"
    os.makedirs(outdir, exist_ok=True)

    sns.set_style("whitegrid", {'axes.facecolor': background})
    plt.style.use("dark_background")

    distances = []
    for dist, count in data.items():
        distances.extend([dist] * count)
    distances = np.array(distances)

    kde = gaussian_kde(distances, bw_method=0.1)
    x_min, x_max = min(distances) - 0.1, max(distances) + 0.1
    x_grid = np.linspace(x_min, x_max, 1000)
    kde_values = kde.evaluate(x_grid)
    scale_factor = 100 / max(data.values()) * 3
    kde_values = kde_values * len(distances) * (x_grid[1] - x_grid[0]) * scale_factor

    # считаем частоты (интенсивности)
    unique, counts = list(data.keys()), list(data.values())

    # нормализация для градиента
    norm = plt.Normalize(vmin=min(counts), vmax=max(counts))
    colors = matplotlib.colormaps.get_cmap(cmap)(norm(counts))

    # строим гистограмму-спектр
    fig, ax = plt.subplots(figsize=(6, 4))
    plt.bar(unique, counts, color=colors, width=0.02, edgecolor="white", linewidth=0.6)
    if kde_values is not None:
        plt.plot(x_grid, kde_values, color='cyan', linewidth=1)
        ax.fill_between(x_grid, kde_values, color="cyan", alpha=0.2)

    plt.xlabel("Расстояние между ионами")
    plt.ylabel("Интенсивность (частота)")
    plt.title(f"Спектр распределения длин векторов\n между ионами относительно иона ({ion[0]},{ion[1]},{ion[2]})")

    plt.tight_layout()
    out_path = os.path.join(outdir, f"spectrum_{substance_id}-{vector_id + 1}.png")
    plt.savefig(out_path, dpi=300)
    plt.close(fig)

    print(f"Изображение spectrum_{substance_id}-{vector_id + 1}.png сохранено!")


def kde_array(data):
    distances = []
    for dist, count in data.items():
        distances.extend([dist] * count)
    distances = np.array(distances)

    kde = gaussian_kde(distances, bw_method=0.1)
    x_min, x_max = 0, 2
    x_grid = np.linspace(x_min, x_max, 200)
    kde_values = kde.evaluate(x_grid)
    return np.array(list(kde_values))
