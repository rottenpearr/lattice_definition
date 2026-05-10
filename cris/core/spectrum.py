import os
from collections import Counter

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import gaussian_kde

from cris.db.connection import get_cursor
from cris.core.coordinates import shift_coordinates, normalize_coordinates
from cris.core.vectors import get_lattice_vectors2


def create_all_spectrum_plots():
    """
    Строит спектры для всех эталонных структур в БД.
    """
    lattice_list = []
    try:
        with get_cursor() as cur:
            cur.execute("SELECT MAX(id) FROM reference_structure")
            lattice_count = cur.fetchone()[0] or 0
            for struct_id in range(1, lattice_count + 1):
                cur.execute(
                    "SELECT structure_id, fract_x, fract_y, fract_z "
                    "FROM structure_site WHERE structure_id = %s",
                    (struct_id,)
                )
                lattice = cur.fetchall()
                if lattice:
                    lattice_list.append(lattice)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    for lattice in lattice_list:
        substance_id = lattice[0][0]

        data_dict = {}
        for i in range(len(lattice)):
            data_dict[i + 1] = lattice[i]
        shifted_data = shift_coordinates(data_dict.values())
        normalized_data = normalize_coordinates(shifted_data)

        vectors = get_lattice_vectors2(normalized_data)
        for id, ion in enumerate(vectors.keys()):
            ion_coords = [float(elem) for elem in ion.split(";")]
            plot_spectra(data=dict(Counter(vectors[ion])), ion=ion_coords, substance_id=substance_id, vector_id=id,
                         cmap="plasma", background="#20232a")

def plot_spectra(data, ion, substance_id, vector_id, cmap="plasma", background="#1e1e1e", outdir="../../data/spectrum"):
    """
    Строит спектры (гистограммы) для набора расстояний между ионами.

    data : list[tuple]
        Набор кортежей с расстояниями
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
        ax.fill_between(x_grid, kde_values, color="cyan", alpha=0.2)  # заливка под кривой

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
