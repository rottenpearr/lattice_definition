import numpy as np
import matplotlib.pyplot as plt
import os


# парсим в формат координат
def parse_xyz_file(filename):
    a = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    # Пропускаем первую строку (количество атомов)
    # Вторая строка содержит информацию о решетке
    lattice_line = lines[1].strip()
    # Извлекаем параметр решетки
    lattice_constant = None
    if 'Lattice=' in lattice_line:
        lattice_parts = lattice_line.split('Lattice="')[1].split('"')[0].split()
        if len(lattice_parts) >= 1:
            lattice_constant = float(lattice_parts[0])

    if lattice_constant is None:
        raise ValueError("Не удалось определить параметр решетки из файла")

    print(f"Параметр решетки: {lattice_constant}")

    # Обрабатываем строки с атомами (начиная с 3-й строки)
    for line in lines[2:]:
        parts = line.strip().split()
        if len(parts) >= 4:
            species = parts[0]
            x = float(parts[1]) / lattice_constant
            y = float(parts[2]) / lattice_constant
            z = float(parts[3]) / lattice_constant
            a.append(['ion', x, y, z])
    return a

# Парсим данные
try:
    a = parse_xyz_file('NaCl_3x3x3.xyz')
    print(f"Парсинг завершен. Создано {len(a)} ионов")
    print(f"Пример первых 5 ионов:")
    for i in range(min(5, len(a))):
        print(f"  {a[i]}")
except FileNotFoundError:
    print("Файл не найден.")

# извлечение координат
def extract_coordinates(structure):
    return np.array([ion[1:] for ion in structure], dtype=float)

def calculate_ion_spectrum(central_ion_coords, all_coords, bins):
    # Вычисляем расстояния от центрального иона до всех остальных
    distances = np.linalg.norm(all_coords - central_ion_coords, axis=1)
    # Убираем расстояние до самого себя (которое равно 0)
    distances = distances[distances > 1e-10]
    # Строим гистограмму
    hist, bin_edges = np.histogram(distances, bins=bins)
    return hist, bin_edges

def create_ion_spectrum_plot(ideal_coords, ion_idx, bins, output_dir):
    # Создаем папку для результатов, если ее нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Вычисляем идеальный спектр для этого иона
    ideal_spectrum, bin_edges = calculate_ion_spectrum(ideal_coords[ion_idx], ideal_coords, bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = np.diff(bin_edges)[0]
    # Создаем график
    plt.figure(figsize=(10, 6))
    # Рисуем идеальный спектр
    plt.bar(bin_centers, ideal_spectrum, width=bin_width,
            alpha=0.8, color='blue', label='Идеальный спектр', edgecolor='white')
    # Настройки графика
    plt.xlabel('Расстояние', fontsize=12)
    plt.ylabel('Количество ионов', fontsize=12)
    plt.title(f'Спектр для иона {ion_idx}\nКоординаты: {ideal_coords[ion_idx].round(3)}', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    # Добавляем информацию о количестве ионов
    total_neighbors = np.sum(ideal_spectrum)
    plt.text(0.02, 0.98, f'Всего соседей: {total_neighbors}', transform=plt.gca().transAxes,
             verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    # Сохраняем график
    filename = os.path.join(output_dir, f'ion_{ion_idx}_spectrum.png')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    return filename

def create_all_ions_summary_plot(ideal_coords, bins, output_dir):
    """Создает сводный график со спектрами всех ионов"""
    plt.figure(figsize=(12, 8))
    n_ions = len(ideal_coords)
    colors = plt.cm.viridis(np.linspace(0, 1, n_ions))
    for ion_idx in range(n_ions):
        # Вычисляем спектр для иона
        spectrum, bin_edges = calculate_ion_spectrum(ideal_coords[ion_idx], ideal_coords, bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        # Рисуем спектр
        plt.plot(bin_centers, spectrum, color=colors[ion_idx], alpha=0.7,
                 label=f'Ион {ion_idx}' if ion_idx < 10 else None)

    plt.xlabel('Расстояние', fontsize=12)
    plt.ylabel('Количество ионов', fontsize=12)
    plt.title('Сводный график спектров всех ионов', fontsize=14)
    plt.legend(ncol=2, fontsize=8)
    plt.grid(True, alpha=0.3)

    filename = os.path.join(output_dir, 'all_ions_summary.png')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

    return filename

def save_coordinates_to_file(ideal_coords, output_dir):
    """Сохраняет координаты ионов в файл"""
    filename = os.path.join(output_dir, 'ideal_coordinates.txt')
    with open(filename, 'w') as f:
        f.write("Идеальные координаты ионов (дробные)\n")
        f.write("=" * 50 + "\n\n")
        for i, coords in enumerate(ideal_coords):
            f.write(f"Ион {i}: {coords[0]:.6f} {coords[1]:.6f} {coords[2]:.6f}\n")
    return filename

# Основной код
ideal_coords = extract_coordinates(a)
n_ions = len(ideal_coords)

print(f"Создан идеальный датасет с {n_ions} ионами")

max_distance = np.sqrt(3)  # максимальное расстояние в кубе 1x1x1
bins = np.linspace(0, max_distance, 25)

# Создаем папку для результатов
output_dir = "ideal_ion_spectra"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Сохраняем координаты
coords_file = save_coordinates_to_file(ideal_coords, output_dir)
print(f"Координаты сохранены в файл: {coords_file}")

# Создаем рисунки для каждого иона
print(f"\nСоздание спектров для {n_ions} ионов...")
ion_info = []

for ion_idx in range(n_ions):
    print(f"Обработка иона {ion_idx + 1}/{n_ions}")
    # Создаем график спектра для иона
    filename = create_ion_spectrum_plot(ideal_coords, ion_idx, bins, output_dir)
    # Сохраняем информацию об ионе
    spectrum, _ = calculate_ion_spectrum(ideal_coords[ion_idx], ideal_coords, bins)
    total_neighbors = np.sum(spectrum)

    ion_info.append({
        'ion_index': ion_idx,
        'coordinates': ideal_coords[ion_idx],
        'spectrum_plot': filename,
        'total_neighbors': total_neighbors
    })

summary_plot = create_all_ions_summary_plot(ideal_coords, bins, output_dir)
print(f"Создан сводный график: {summary_plot}")

summary_filename = os.path.join(output_dir, "summary.txt")
with open(summary_filename, 'w') as f:
    f.write("Сводная информация по анализам спектров ионов\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Всего ионов: {n_ions}\n")
    f.write(f"Идеальная решетка (без шума)\n\n")

    for info in ion_info:
        f.write(f"Ион {info['ion_index']}: координаты {info['coordinates']}\n")
        f.write(f"  Всего соседей: {info['total_neighbors']}\n")
        f.write(f"  График спектра: {info['spectrum_plot']}\n")
        f.write("-" * 40 + "\n")

print(f"\nГотово! Создано {n_ions + 1} рисунков.")
print(f"Для каждого иона создан индивидуальный график спектра")
print(f"Создан сводный график всех спектров")
print(f"Результаты сохранены в папке: {output_dir}")
print(f"Сводная информация: {summary_filename}")

# Показываем пример первого иона
print(f"\nПример для иона 0:")
print(f"Координаты: {ideal_coords[0]}")
print(f"Всего соседей: {ion_info[0]['total_neighbors']}")
print(f"Файл: ion_0_spectrum.png")