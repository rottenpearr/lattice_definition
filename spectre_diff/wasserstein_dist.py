import numpy as np
from scipy.stats import wasserstein_distance
import matplotlib.pyplot as plt
import random
import os

# Идеальная решетка (взята из тестовых в scripts/operations/lattice_microoperations.py)
a = [['ion', 0.25, 0.25, 0.25], ['ion', 0.25, 0.25, 0.75], ['ion', 0.25, 0.75, 0.25], ['ion', 0.25, 0.75, 0.75],
     ['ion', 0.75, 0.25, 0.25], ['ion', 0.75, 0.25, 0.75], ['ion', 0.75, 0.75, 0.25], ['ion', 0.75, 0.75, 0.75],
     ['ion', 0.25, 0.5, 0.5], ['ion', 0.75, 0.5, 0.5], ['ion', 0.5, 0.25, 0.5], ['ion', 0.5, 0.75, 0.5],
     ['ion', 0.5, 0.5, 0.25], ['ion', 0.5, 0.5, 0.75], ['ion', 0.5, 0.5, 0.5], ['ion', 0.5, 0.25, 0.25],
     ['ion', 0.5, 0.25, 0.75], ['ion', 0.5, 0.75, 0.25], ['ion', 0.5, 0.75, 0.75], ['ion', 0.25, 0.5, 0.25],
     ['ion', 0.25, 0.5, 0.75], ['ion', 0.75, 0.5, 0.25], ['ion', 0.75, 0.5, 0.75], ['ion', 0.25, 0.25, 0.5],
     ['ion', 0.25, 0.75, 0.5], ['ion', 0.75, 0.25, 0.5], ['ion', 0.75, 0.75, 0.5], ['ion', 0.0, 0.25, 0.25],
     ['ion', 0.25, 0.0, 0.25], ['ion', 0.25, 0.25, 0.0], ['ion', 0.0, 0.25, 0.75], ['ion', 0.25, 0.0, 0.75],
     ['ion', 0.25, 0.25, 1.0], ['ion', 0.0, 0.75, 0.25], ['ion', 0.25, 0.75, 0.0], ['ion', 0.25, 1.0, 0.25],
     ['ion', 0.0, 0.75, 0.75], ['ion', 0.25, 0.75, 1.0], ['ion', 0.25, 1.0, 0.75], ['ion', 0.75, 0.0, 0.25],
     ['ion', 0.75, 0.25, 0.0], ['ion', 1.0, 0.25, 0.25], ['ion', 0.75, 0.0, 0.75], ['ion', 0.75, 0.25, 1.0],
     ['ion', 1.0, 0.25, 0.75], ['ion', 0.75, 0.75, 0.0], ['ion', 0.75, 1.0, 0.25], ['ion', 1.0, 0.75, 0.25],
     ['ion', 0.75, 0.75, 1.0], ['ion', 0.75, 1.0, 0.75], ['ion', 1.0, 0.75, 0.75], ['ion', 0.0, 0.5, 0.5],
     ['ion', 1.0, 0.5, 0.5], ['ion', 0.5, 0.0, 0.5], ['ion', 0.5, 1.0, 0.5], ['ion', 0.5, 0.5, 0.0],
     ['ion', 0.5, 0.5, 1.0]]

# извлечение координат
def extract_coordinates(structure):
    return np.array([ion[1:] for ion in structure], dtype=float)

def calculate_ion_spectrum(central_ion_coords, all_coords, bins):
    """Вычисляет спектр для одного иона: количество ионов на каждом расстоянии"""
    # Вычисляем расстояния от центрального иона до всех остальных
    distances = np.linalg.norm(all_coords - central_ion_coords, axis=1)

    # Убираем расстояние до самого себя (которое равно 0)
    distances = distances[distances > 1e-10]

    # Строим гистограмму
    hist, bin_edges = np.histogram(distances, bins=bins)
    return hist, bin_edges

# добавляем к координатам погрешность
def add_noise_to_structure(structure, noise_level=0.05):
    noisy_structure = []
    for ion in structure:
        noisy_coords = [ion[0]]  # сохраняем название иона
        for coord in ion[1:]:
            # Добавляем случайный шум в пределах ±noise_level
            noise = random.uniform(-noise_level, noise_level)
            noisy_coord = coord + noise
            # Обеспечиваем периодические граничные условия [0, 1]
            noisy_coord = noisy_coord % 1.0
            noisy_coords.append(noisy_coord)
        noisy_structure.append(noisy_coords)
    return noisy_structure

def create_ion_spectrum_plots_separate(ideal_coords, noisy_coords_dict, ion_idx, bins, output_dir):
    """Создает отдельные графики для каждого уровня шума на одном рисунке"""

    # Создаем папку для результатов, если ее нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Вычисляем идеальный спектр для этого иона
    ideal_spectrum, bin_edges = calculate_ion_spectrum(ideal_coords[ion_idx], ideal_coords, bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = np.diff(bin_edges)[0]

    # Уровни шума и цвета
    noise_levels = [0.02, 0.05, 0.07, 0.10]
    colors = ['red', 'blue', 'green', 'orange']

    # Создаем большой рисунок с несколькими subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.flatten()

    # Общий заголовок для всего рисунка
    fig.suptitle(f'Спектры для иона {ion_idx}\nКоординаты: {ideal_coords[ion_idx].round(3)}',
                 fontsize=16, fontweight='bold')

    # Рисуем каждый уровень шума на отдельном subplot
    for i, (noise_level, color) in enumerate(zip(noise_levels, colors)):
        noisy_coords = noisy_coords_dict[noise_level]
        noisy_spectrum, _ = calculate_ion_spectrum(noisy_coords[ion_idx], noisy_coords, bins)

        # Вычисляем EMD (расстояние Вассерштейна)
        emd = wasserstein_distance(bin_centers, bin_centers, ideal_spectrum, noisy_spectrum)

        # Рисуем на соответствующем subplot
        ax = axes[i]

        # Идеальный спектр
        ax.bar(bin_centers, ideal_spectrum, width=bin_width,
               alpha=0.6, color='black', label='Идеальный', edgecolor='white')

        # Зашумленный спектр
        ax.bar(bin_centers, noisy_spectrum, width=bin_width,
               alpha=0.6, color=color, label=f'Шум {noise_level * 100:.0f}%', edgecolor='white')

        # Настройки subplot
        ax.set_xlabel('Расстояние', fontsize=10)
        ax.set_ylabel('Количество ионов', fontsize=10)
        ax.set_title(f'Шум {noise_level * 100:.0f}%: EMD = {emd:.4f}', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Добавляем текстовую информацию
        ax.text(0.02, 0.98, f'EMD = {emd:.4f}', transform=ax.transAxes,
                verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Добавляем общий идеальный спектр для сравнения
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)

    # Сохраняем график
    filename = os.path.join(output_dir, f'ion_{ion_idx}_spectra_separate.png')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

    return filename

def create_combined_comparison_plot(ideal_coords, noisy_coords_dict, ion_idx, bins, output_dir):
    """Создает дополнительный график с сравнением всех спектров на одном plot"""

    # Вычисляем идеальный спектр
    ideal_spectrum, bin_edges = calculate_ion_spectrum(ideal_coords[ion_idx], ideal_coords, bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Создаем график
    plt.figure(figsize=(12, 8))

    # Рисуем идеальный спектр
    plt.bar(bin_centers, ideal_spectrum, width=np.diff(bin_edges)[0],
            alpha=0.8, color='black', label='Идеальный', edgecolor='white')

    # Уровни шума и цвета
    noise_levels = [0.02, 0.05, 0.07, 0.10]
    colors = ['red', 'blue', 'green', 'orange']
    line_styles = ['-', '--', '-.', ':']

    # Рисуем зашумленные спектры линиями
    for i, (noise_level, color, line_style) in enumerate(zip(noise_levels, colors, line_styles)):
        noisy_coords = noisy_coords_dict[noise_level]
        noisy_spectrum, _ = calculate_ion_spectrum(noisy_coords[ion_idx], noisy_coords, bins)

        # Вычисляем EMD
        emd = wasserstein_distance(bin_centers, bin_centers, ideal_spectrum, noisy_spectrum)

        plt.plot(bin_centers, noisy_spectrum, line_style, color=color,
                 linewidth=2, label=f'Шум {noise_level * 100:.0f}% (EMD={emd:.3f})')

    # Настройки графика
    plt.xlabel('Расстояние', fontsize=12)
    plt.ylabel('Количество ионов', fontsize=12)
    plt.title(f'Сравнение спектров для иона {ion_idx}\nКоординаты: {ideal_coords[ion_idx].round(3)}', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Сохраняем график
    filename = os.path.join(output_dir, f'ion_{ion_idx}_comparison.png')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

    return filename


# Основной код
ideal_coords = extract_coordinates(a)
n_ions = len(ideal_coords)

# Уровни шума для анализа
noise_levels = [0.02, 0.05, 0.07, 0.10]
noisy_coords_dict = {}

# Генерируем зашумленные решетки для каждого уровня шума
print("Генерация зашумленных решеток...")
for noise_level in noise_levels:
    noisy_structure = add_noise_to_structure(a, noise_level)
    noisy_coords_dict[noise_level] = extract_coordinates(noisy_structure)
    print(f"Создана решетка с шумом {noise_level * 100:.0f}%")

# Создаем бины для гистограмм
max_distance = np.sqrt(3)  # максимальное расстояние в кубе 1x1x1
bins = np.linspace(0, max_distance, 25)  # 25 бинов для лучшей видимости

# Создаем папку для результатов
output_dir = "ion_spectra_separate"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Создаем рисунки для каждого иона
print(f"\nСоздание рисунков для {n_ions} ионов...")
ion_info = []

for ion_idx in range(n_ions):
    print(f"Обработка иона {ion_idx + 1}/{n_ions}")

    # Создаем основной рисунок с отдельными subplots
    filename1 = create_ion_spectrum_plots_separate(ideal_coords, noisy_coords_dict, ion_idx, bins, output_dir)

    # Создаем дополнительный рисунок с сравнением на одном plot
    filename2 = create_combined_comparison_plot(ideal_coords, noisy_coords_dict, ion_idx, bins, output_dir)

    # Сохраняем информацию об ионе
    ion_info.append({
        'ion_index': ion_idx,
        'coordinates': ideal_coords[ion_idx],
        'separate_plot': filename1,
        'comparison_plot': filename2
    })

# Создаем summary-файл
summary_filename = os.path.join(output_dir, "summary.txt")
with open(summary_filename, 'w') as f:
    f.write("Сводная информация по анализам спектров ионов\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Всего ионов: {n_ions}\n")
    f.write(f"Уровни шума: {[f'{nl * 100:.0f}%' for nl in noise_levels]}\n\n")

    for info in ion_info:
        f.write(f"Ион {info['ion_index']}: координаты {info['coordinates']}\n")
        f.write(f"Отдельные графики: {info['separate_plot']}\n")
        f.write(f"График сравнения: {info['comparison_plot']}\n")
        f.write("-" * 40 + "\n")

print(f"\nГотово! Создано {n_ions * 2} рисунков.")
print(f"Для каждого иона создано:")
print(f"  1. Основной рисунок с 4 отдельными графиками")
print(f"  2. Дополнительный рисунок со сравнением на одном графике")
print(f"Результаты сохранены в папке: {output_dir}")
print(f"Сводная информация: {summary_filename}")

# Показываем пример первого иона
print(f"\nПример для иона 0:")
print(f"Координаты: {ideal_coords[0]}")
print(f"Файлы: ion_0_spectra_separate.png, ion_0_comparison.png")