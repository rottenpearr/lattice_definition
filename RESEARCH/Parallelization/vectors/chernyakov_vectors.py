import os
import time
from multiprocessing import Pool, cpu_count

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import gaussian_kde


def process_ion_batch(args):
    """
    Вычисляет расстояния для пакета ионов до всех остальных.
    Функция для параллельного выполнения.

    Args:
        args: кортеж (ion_indices, elements, coords, all_coords, all_elements)

    Returns:
        list: список пар (ion_key, distances) для каждого иона в пакете
    """
    ion_indices, elements_batch, coords_batch, all_coords, all_elements = args
    results = []

    for idx, element, coord in zip(ion_indices, elements_batch, coords_batch):
        x, y, z = coord
        ion_key = f"{element};{x:.8f};{y:.8f};{z:.8f}"

        distances = []
        n_ions = len(all_coords)

        for j in range(n_ions):
            if idx != j:
                # Разность координат
                dx = all_coords[j, 0] - x
                dy = all_coords[j, 1] - y
                dz = all_coords[j, 2] - z

                # При необходимости можно учесть периодические граничные условия:
                # dx = dx - np.round(dx)
                # dy = dy - np.round(dy)
                # dz = dz - np.round(dz)

                # Вычисляем расстояние
                distance = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
                distances.append(distance)

        results.append((ion_key, distances))

    return results


def get_lattice_vectors_parallel(lattice_data, n_processes=None):
    """
    Параллелизованная версия вычисления векторов для ВСЕХ ионов решетки.
    Ионы распределяются по процессам пакетами размером ~N/M.

    Args:
        lattice_data: список ионов в формате [['Element', x, y, z], ...]
        n_processes: количество процессов (None = автоматически)

    Returns:
        dict: словарь где ключи - уникальные идентификаторы ионов,
              значения - списки расстояний до всех других ионов
    """
    # Конвертируем данные в numpy массив для эффективности
    elements = [ion[0] for ion in lattice_data]
    coords = np.array([ion[1:4] for ion in lattice_data])

    n_ions = len(lattice_data)

    # Определяем количество процессов
    if n_processes is None:
        n_processes = cpu_count()

    # Вычисляем размер пакета для каждого процесса
    chunk_size = n_ions // n_processes
    remainder = n_ions % n_processes

    # Подготовка пакетов задач для параллельной обработки
    args_list = []
    start_idx = 0

    for i in range(n_processes):
        # Распределяем остаток по первым процессам
        current_chunk_size = chunk_size + (1 if i < remainder else 0)
        end_idx = start_idx + current_chunk_size

        if start_idx < n_ions:
            ion_indices = list(range(start_idx, end_idx))
            elements_batch = [elements[j] for j in ion_indices]
            coords_batch = coords[ion_indices]

            args_list.append((
                ion_indices,
                elements_batch,
                coords_batch,
                coords,
                elements
            ))

        start_idx = end_idx

    # Параллельное вычисление
    with Pool(processes=n_processes) as pool:
        batch_results = pool.map(process_ion_batch, args_list)

    # Собираем результаты в словарь
    all_vectors = {}
    for batch in batch_results:
        for ion_key, distances in batch:
            all_vectors[ion_key] = distances

    return all_vectors


def plot_spectra(data, ion, substance_id, vector_id, cmap="plasma",
                 background="#1e1e1e", outdir="./data/spectrum"):
    """
    Строит спектры (гистограммы) для набора расстояний между ионами.

    data : dict
        Словарь с расстояниями и их количеством
    ion : tuple
        Координаты иона
    substance_id : str/int
        Идентификатор вещества
    vector_id : int
        Идентификатор набора векторов
    cmap : str
        Цветовая схема для градиента
    background : str
        Цвет фона графиков
    outdir : str
        Директория для сохранения
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

    unique, counts = list(data.keys()), list(data.values())

    norm = plt.Normalize(vmin=min(counts), vmax=max(counts))
    colors = matplotlib.colormaps.get_cmap(cmap)(norm(counts))

    fig, ax = plt.subplots(figsize=(6, 4))
    plt.bar(unique, counts, color=colors, width=0.02, edgecolor="white", linewidth=0.6)
    if kde_values is not None:
        plt.plot(x_grid, kde_values, color='cyan', linewidth=1)
        ax.fill_between(x_grid, kde_values, color="cyan", alpha=0.2)

    plt.xlabel("Расстояние между ионами")
    plt.ylabel("Интенсивность (частота)")
    plt.title(f"Спектр распределения длин векторов\nмежду ионами относительно иона ({ion[0]},{ion[1]},{ion[2]})")

    plt.tight_layout()
    out_path = os.path.join(outdir, f"spectrum_{substance_id}-{vector_id + 1}.png")
    plt.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"Изображение spectrum_{substance_id}-{vector_id + 1}.png сохранено!")


def generate_test_lattice(n_ions=100):
    """
    Генерирует тестовую кристаллическую решетку.

    Args:
        n_ions: количество ионов

    Returns:
        list: список ионов [['Element', x, y, z], ...]
    """
    elements = ['Na', 'Cl']
    lattice_data = []

    np.random.seed(42)
    for i in range(n_ions):
        element = elements[i % 2]
        x, y, z = np.random.random(3)
        lattice_data.append([element, x, y, z])

    return lattice_data


def benchmark_scalability(lattice_data, max_processes=24):
    """
    Тестирует масштабируемость для различного количества потоков.

    Args:
        lattice_data: данные решетки
        max_processes: максимальное количество процессов для тестирования

    Returns:
        dict: результаты бенчмарков
    """
    print(f"Доступно CPU ядер: {cpu_count()}")
    print(f"Размер решетки: {len(lattice_data)} ионов")
    print(f"Тестирование масштабируемости от 1 до {max_processes} потоков...\n")

    results = {
        'processes': [],
        'real_time': [],
        'speedup': [],
        'efficiency': []
    }

    # Измерение времени для последовательного выполнения (базовое)
    print("=" * 60)
    print(f"Тест 1: Последовательное выполнение")
    print("=" * 60)
    start_time = time.time()
    vectors_par = get_lattice_vectors_parallel(lattice_data, n_processes=1)
    t1 = time.time() - start_time
    print(f"Время выполнения: {t1:.4f} секунд")
    print(f"Вычислено векторов для {len(vectors_par)} ионов\n")

    results['processes'].append(1)
    results['real_time'].append(t1)
    results['speedup'].append(1.0)
    results['efficiency'].append(1.0)

    # Тестирование для 2-max_processes потоков
    for n_proc in range(2, max_processes + 1):
        print("=" * 60)
        print(f"Тест {n_proc}: Параллельное выполнение ({n_proc} потоков)")
        print("=" * 60)

        start_time = time.time()
        vectors_par = get_lattice_vectors_parallel(lattice_data, n_processes=n_proc)
        real_time = time.time() - start_time

        speedup = t1 / real_time
        efficiency = speedup / n_proc

        results['processes'].append(n_proc)
        results['real_time'].append(real_time)
        results['speedup'].append(speedup)
        results['efficiency'].append(efficiency)

        print(f"Время выполнения: {real_time:.4f} секунд")
        print(f"Ускорение: {speedup:.2f}x")
        print(f"Эффективность: {efficiency:.2%}")
        print(f"Вычислено векторов для {len(vectors_par)} ионов\n")

    return results


def plot_scalability(results, output_dir="./data/benchmarks"):
    """
    Строит график масштабируемости (только время выполнения).

    Args:
        results: результаты бенчмарков
        output_dir: директория для сохранения графиков
    """
    os.makedirs(output_dir, exist_ok=True)

    processes = np.array(results['processes'])
    real_time = np.array(results['real_time'])
    t1 = real_time[0]
    ideal_time = t1 / processes

    # График: Реальное vs Идеальное время
    plt.figure(figsize=(12, 7))
    plt.plot(processes, real_time, 'o-', linewidth=2.5, markersize=10,
             label='Реальное время', color='#e74c3c')
    plt.plot(processes, ideal_time, 's--', linewidth=2.5, markersize=9,
             label='Идеальное время (T1/M)', color='#3498db')

    plt.xlabel('Количество потоков (M)', fontsize=14, fontweight='bold')
    plt.ylabel('Время выполнения (секунды)', fontsize=14, fontweight='bold')
    plt.title('Масштабируемость параллельных вычислений межатомных расстояний',
              fontsize=16, fontweight='bold', pad=20)
    plt.legend(fontsize=13, loc='best')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()

    plt.savefig(os.path.join(output_dir, 'scalability.png'), dpi=150)
    print(f"График сохранен: {output_dir}/scalability.png")
    plt.close()


def main():
    """
    Главная функция для запуска тестирования.
    """
    print("\n" + "=" * 60)
    print("ПАРАЛЛЕЛИЗАЦИЯ ВЫЧИСЛЕНИЙ МЕЖАТОМНЫХ РАССТОЯНИЙ")
    print("=" * 60 + "\n")

    # Генерация тестовых данных
    # Можно изменить n_ions для разного размера задачи
    n_ions = 2000  # Увеличьте для более продолжительных вычислений
    lattice_data = generate_test_lattice(n_ions)

    # Тестирование масштабируемости
    max_processes = 24  # Тестируем до 24 потоков
    results = benchmark_scalability(lattice_data, max_processes=max_processes)

    # Построение графиков
    print("\n" + "=" * 60)
    print("ПОСТРОЕНИЕ ГРАФИКОВ МАСШТАБИРУЕМОСТИ")
    print("=" * 60 + "\n")
    plot_scalability(results)

    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)
    print(
        f"\nЛучшее ускорение: {max(results['speedup']):.2f}x при {results['processes'][results['speedup'].index(max(results['speedup']))]} потоках")
    print(
        f"Лучшая эффективность: {max(results['efficiency']):.2%} при {results['processes'][results['efficiency'].index(max(results['efficiency']))]} потоках")


if __name__ == "__main__":
    main()
