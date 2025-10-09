from collections import defaultdict
from math import sqrt
import numpy as np

def get_lattice_vectors(normalized_data):
    """
    Функция получает на вход нормализованные координаты ионов и находит всевозможные n * (n - 1) / 2 векторов расстояний между всеми ионами без повторов.
    :param normalized_data: Список нормализованных координат ионов вида [['ion', 0.5, 0.0, 0.5], ['ion', 0.5, 1.0, 0.5], ['ion', 0.5, 0.5, 0.0], ...]
    :return: dict of vectors
    """
    ion_amount = len(normalized_data)
    vector_dict = defaultdict(int)
    for i in range(ion_amount):
        ion1, x1, y1, z1 = normalized_data[i]
        for j in range(i + 1, ion_amount):
            ion2, x2, y2, z2 = normalized_data[j]
            ion_distance = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
            vector_dict[ion_distance] += 1
    return vector_dict


def get_lattice_vectors2(normalized_data):
    """
    Функция получает на вход нормализованные координаты ионов и находит всевозможные n * (n - 1) векторов расстояний между всеми ионами с повторами.
    :param normalized_data: list
        Список нормализованных координат ионов вида [['ion', 0.5, 0.0, 0.5], ['ion', 0.5, 1.0, 0.5], ['ion', 0.5, 0.5, 0.0], ...]
    :return: set
        Множество списков векторов
    """
    ion_amount = len(normalized_data)
    vector_set = set()
    res = defaultdict(tuple)
    for i in range(ion_amount):
        ion1, x1, y1, z1 = normalized_data[i]
        vectors = []
        for j in range(ion_amount):
            if j == i:
                continue
            ion2, x2, y2, z2 = normalized_data[j]
            ion_distance = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
            vectors.append(ion_distance)
        vectors.sort()  # это плохо МИНУС МНОГО ВРЕМЕНИ
        vector_tuple = tuple(vectors)
        vector_dict_len = len(vector_set)
        vector_set.add(vector_tuple)
        if len(vector_set) != vector_dict_len:
            res[f"{x1};{y1};{z1}"] = vector_tuple  # чутка дублируем значения с vector_set
    return res


def get_lattice_vectors3(lattice_data):
    """
    Вычисляет векторы для ВСЕХ ионов решетки (не группируя по уникальным позициям)

    Args:
        lattice_data: список ионов в формате [['Element', x, y, z], ...]

    Returns:
        dict: словарь где ключи - уникальные идентификаторы ионов,
              значения - списки расстояний до всех других ионов
    """

    # Конвертируем данные в numpy массив для эффективности
    elements = [ion[0] for ion in lattice_data]
    coords = np.array([ion[1:4] for ion in lattice_data])

    n_ions = len(lattice_data)
    all_vectors = {}

    print(f"Вычисление векторов для {n_ions} ионов...")

    for i in range(n_ions):
        # Создаем уникальный ключ для иона
        element = elements[i]
        x, y, z = coords[i]
        ion_key = f"{element};{x:.8f};{y:.8f};{z:.8f}"

        distances = []

        # Вычисляем расстояния до всех других ионов
        for j in range(n_ions):
            if i != j:  # исключаем расстояние до самого себя
                # Разность координат
                dx = coords[j, 0] - x
                dy = coords[j, 1] - y
                dz = coords[j, 2] - z

                # Учет периодических граничных условий (минимальное изображение)
                dx = dx - np.round(dx)
                dy = dy - np.round(dy)
                dz = dz - np.round(dz)

                # Вычисляем расстояние
                distance = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
                distances.append(distance)

        all_vectors[ion_key] = distances

    print(f"Вычислено векторов для {len(all_vectors)} ионов")

    # Проверим распределение по типам ионов
    element_count = defaultdict(int)
    for key in all_vectors.keys():
        element = key.split(';')[0]
        element_count[element] += 1

    print(f"Распределение ионов: {dict(element_count)}")

    return all_vectors



# Тестовые данные:
# a = [['ion', 0.25, 0.25, 0.25], ['ion', 0.25, 0.25, 0.75], ['ion', 0.25, 0.75, 0.25], ['ion', 0.25, 0.75, 0.75], ['ion', 0.75, 0.25, 0.25], ['ion', 0.75, 0.25, 0.75], ['ion', 0.75, 0.75, 0.25], ['ion', 0.75, 0.75, 0.75], ['ion', 0.25, 0.5, 0.5], ['ion', 0.75, 0.5, 0.5], ['ion', 0.5, 0.25, 0.5], ['ion', 0.5, 0.75, 0.5], ['ion', 0.5, 0.5, 0.25], ['ion', 0.5, 0.5, 0.75], ['ion', 0.5, 0.5, 0.5], ['ion', 0.5, 0.25, 0.25], ['ion', 0.5, 0.25, 0.75], ['ion', 0.5, 0.75, 0.25], ['ion', 0.5, 0.75, 0.75], ['ion', 0.25, 0.5, 0.25], ['ion', 0.25, 0.5, 0.75], ['ion', 0.75, 0.5, 0.25], ['ion', 0.75, 0.5, 0.75], ['ion', 0.25, 0.25, 0.5], ['ion', 0.25, 0.75, 0.5], ['ion', 0.75, 0.25, 0.5], ['ion', 0.75, 0.75, 0.5], ['ion', 0.0, 0.25, 0.25], ['ion', 0.25, 0.0, 0.25], ['ion', 0.25, 0.25, 0.0], ['ion', 0.0, 0.25, 0.75], ['ion', 0.25, 0.0, 0.75], ['ion', 0.25, 0.25, 1.0], ['ion', 0.0, 0.75, 0.25], ['ion', 0.25, 0.75, 0.0], ['ion', 0.25, 1.0, 0.25], ['ion', 0.0, 0.75, 0.75], ['ion', 0.25, 0.75, 1.0], ['ion', 0.25, 1.0, 0.75], ['ion', 0.75, 0.0, 0.25], ['ion', 0.75, 0.25, 0.0], ['ion', 1.0, 0.25, 0.25], ['ion', 0.75, 0.0, 0.75], ['ion', 0.75, 0.25, 1.0], ['ion', 1.0, 0.25, 0.75], ['ion', 0.75, 0.75, 0.0], ['ion', 0.75, 1.0, 0.25], ['ion', 1.0, 0.75, 0.25], ['ion', 0.75, 0.75, 1.0], ['ion', 0.75, 1.0, 0.75], ['ion', 1.0, 0.75, 0.75], ['ion', 0.0, 0.5, 0.5], ['ion', 1.0, 0.5, 0.5], ['ion', 0.5, 0.0, 0.5], ['ion', 0.5, 1.0, 0.5], ['ion', 0.5, 0.5, 0.0], ['ion', 0.5, 0.5, 1.0]]
#res = get_lattice_vectors(a)
#res2 = sorted(res)
#count = 0
#for elem in res2:
#    print(elem, res[elem])
#    count += res[elem]
#print(count)

