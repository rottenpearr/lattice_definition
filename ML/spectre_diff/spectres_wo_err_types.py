import numpy as np
import matplotlib.pyplot as plt
import os
from collections import defaultdict


# Чтение данных из файла
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
            a.append([species, x, y, z])  # Сохраняем тип иона
    return a, lattice_constant

# Парсим данные
try:
    a, lattice_constant = parse_xyz_file('NaCl_3x3x3.xyz')
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

def spectra_are_identical(spectrum1, spectrum2, tolerance=1e-10):
    return np.allclose(spectrum1, spectrum2, atol=tolerance)

# группировка ионов по типам спектров
def group_ions_by_spectrum(ideal_coords, bins):
    spectrum_groups = defaultdict(list)
    spectra_list = []
    # Вычисляем спектры для всех ионов
    for ion_idx in range(len(ideal_coords)):
        spectrum, _ = calculate_ion_spectrum(ideal_coords[ion_idx], ideal_coords, bins)
        spectra_list.append(spectrum)

    # Группируем ионы по спектрам
    for ion_idx, spectrum in enumerate(spectra_list):
        spectrum_found = False
        for existing_spectrum in spectrum_groups:
            if spectra_are_identical(spectrum, existing_spectrum):
                spectrum_groups[existing_spectrum].append(ion_idx)
                spectrum_found = True
                break
        if not spectrum_found:
            spectrum_groups[tuple(spectrum)].append(ion_idx)
    return spectrum_groups

def get_ion_type_name(coords, species, lattice_constant):
    # Преобразуем обратно в абсолютные координаты для лучшего определения
    abs_x = coords[0] * lattice_constant
    abs_y = coords[1] * lattice_constant
    abs_z = coords[2] * lattice_constant
    # Центральный ион
    if np.allclose([abs_x, abs_y, abs_z], [8.4603, 8.4603, 8.4603], atol=0.1):
        return f"Центральный {species}"
    corner_tol = 0.1
    is_corner = (abs_x < corner_tol or abs_x > lattice_constant - corner_tol) and \
                (abs_y < corner_tol or abs_y > lattice_constant - corner_tol) and \
                (abs_z < corner_tol or abs_z > lattice_constant - corner_tol)
    if is_corner:
        return f"Угловой {species}"
    face_tol = 0.1
    face_count = 0
    for coord in [abs_x, abs_y, abs_z]:
        if coord < face_tol or coord > lattice_constant - face_tol:
            face_count += 1

    if face_count == 1:
        return f"Ион на грани {species}"

    if face_count == 2:
        return f"Ион на ребре {species}"

    return f"Внутренний {species}"


def create_spectrum_type_plot(spectrum, bin_edges, ion_indices, ideal_coords, a, output_dir, type_name):
    """Создает график для типа спектра"""
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = np.diff(bin_edges)[0]
    # Создаем график
    plt.figure(figsize=(12, 8))
    # Рисуем спектр
    plt.bar(bin_centers, spectrum, width=bin_width,
            alpha=0.8, color='blue', label=f'Спектр типа: {type_name}', edgecolor='white')
    # Настройки графика
    plt.xlabel('Расстояние (в единицах решетки)', fontsize=12)
    plt.ylabel('Количество ионов', fontsize=12)
    plt.title(f'Спектр типа: {type_name}\nКоличество ионов: {len(ion_indices)}', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    # Добавляем информацию
    total_neighbors = np.sum(spectrum)
    plt.text(0.02, 0.98, f'Всего соседей: {total_neighbors}\nИонов этого типа: {len(ion_indices)}',
             transform=plt.gca().transAxes, verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    # Сохраняем график
    safe_type_name = type_name.replace(" ", "_").replace("/", "_")
    filename = os.path.join(output_dir, f'spectrum_type_{safe_type_name}.png')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    return filename

def save_spectrum_types_info(spectrum_groups, ideal_coords, a, lattice_constant, output_dir):
    """Сохраняет информацию о типах спектров"""
    filename = os.path.join(output_dir, 'spectrum_types_info.txt')

    with open(filename, 'w') as f:
        f.write("Типы спектров ионов\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Всего ионов: {len(ideal_coords)}\n")
        f.write(f"Параметр решетки: {lattice_constant}\n\n")

        for i, (spectrum_tuple, ion_indices) in enumerate(spectrum_groups.items()):
            spectrum = np.array(spectrum_tuple)
            representative_ion = ion_indices[0]
            coords = ideal_coords[representative_ion]
            species = a[representative_ion][0]
            ion_type = get_ion_type_name(coords, species, lattice_constant)

            f.write(f"Тип {i + 1}: {ion_type}\n")
            f.write(f"Количество ионов: {len(ion_indices)}\n")
            f.write(f"Координаты представителя: {coords}\n")
            f.write(f"Абсолютные координаты: {coords * lattice_constant}\n")
            f.write(f"Тип иона: {species}\n")
            f.write(f"Индексы ионов: {ion_indices}\n")
            f.write(f"Спектр: {spectrum}\n")
            f.write("-" * 50 + "\n")

    return filename

ideal_coords = extract_coordinates(a)
n_ions = len(ideal_coords)

print(f"Создан идеальный датасет с {n_ions} ионами")

max_distance = np.sqrt(3)  # максимальное расстояние в кубе 1x1x1
bins = np.linspace(0, max_distance, 25)

# Создаем папку для результатов
output_dir = "unique_ion_spectra"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Группируем ионы по типам спектров
print("Группировка ионов по типам спектров...")
spectrum_groups = group_ions_by_spectrum(ideal_coords, bins)

print(f"Найдено {len(spectrum_groups)} уникальных типов спектров:")

# Создаем графики для каждого типа спектра
spectrum_info = []

for spectrum_tuple, ion_indices in spectrum_groups.items():
    spectrum = np.array(spectrum_tuple)
    representative_ion = ion_indices[0]
    coords = ideal_coords[representative_ion]
    species = a[representative_ion][0]

    # Определяем тип иона
    ion_type = get_ion_type_name(coords, species, lattice_constant)

    print(f"Тип '{ion_type}': {len(ion_indices)} ионов")

    # Вычисляем bin_edges для графика
    _, bin_edges = calculate_ion_spectrum(ideal_coords[representative_ion], ideal_coords, bins)

    # Создаем график
    filename = create_spectrum_type_plot(spectrum, bin_edges, ion_indices, ideal_coords, a, output_dir, ion_type)

    spectrum_info.append({
        'type_name': ion_type,
        'spectrum': spectrum,
        'ion_indices': ion_indices,
        'representative_coords': coords,
        'species': species,
        'plot_filename': filename
    })

# Сохраняем информацию о типах спектров
info_file = save_spectrum_types_info(spectrum_groups, ideal_coords, a, lattice_constant, output_dir)

# Создаем summary-файл
summary_filename = os.path.join(output_dir, "summary.txt")
with open(summary_filename, 'w') as f:
    f.write("Сводная информация по уникальным спектрам ионов\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Всего ионов: {n_ions}\n")
    f.write(f"Уникальных типов спектров: {len(spectrum_groups)}\n")
    f.write(f"Параметр решетки: {lattice_constant}\n\n")

    for info in spectrum_info:
        f.write(f"Тип: {info['type_name']}\n")
        f.write(f"Количество ионов: {len(info['ion_indices'])}\n")
        f.write(f"Тип иона: {info['species']}\n")
        f.write(f"Координаты представителя: {info['representative_coords']}\n")
        f.write(f"Абсолютные координаты: {info['representative_coords'] * lattice_constant}\n")
        f.write(f"Индексы ионов: {info['ion_indices']}\n")
        f.write(f"График: {info['plot_filename']}\n")
        f.write(f"Сумма спектра: {np.sum(info['spectrum'])}\n")
        f.write("-" * 50 + "\n")

print(f"\nГотово! Создано {len(spectrum_groups)} уникальных графиков спектров.")
print(f"Результаты сохранены в папке: {output_dir}")
print(f"Информация о типах: {info_file}")
print(f"Сводная информация: {summary_filename}")

# Показываем статистику
print(f"\nСтатистика:")
total_count = 0
for info in spectrum_info:
    print(f"  {info['type_name']}: {len(info['ion_indices'])} ионов")
    total_count += len(info['ion_indices'])

print(f"Всего учтено ионов: {total_count}/{n_ions}")