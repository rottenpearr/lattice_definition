from collections import defaultdict
from math import sqrt

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
    vector_dict = set()
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
        vector_dict.add(tuple(vectors))
    return vector_dict



# Тестовые данные:
a = [['ion', 0.25, 0.25, 0.25], ['ion', 0.25, 0.25, 0.75], ['ion', 0.25, 0.75, 0.25], ['ion', 0.25, 0.75, 0.75], ['ion', 0.75, 0.25, 0.25], ['ion', 0.75, 0.25, 0.75], ['ion', 0.75, 0.75, 0.25], ['ion', 0.75, 0.75, 0.75], ['ion', 0.25, 0.5, 0.5], ['ion', 0.75, 0.5, 0.5], ['ion', 0.5, 0.25, 0.5], ['ion', 0.5, 0.75, 0.5], ['ion', 0.5, 0.5, 0.25], ['ion', 0.5, 0.5, 0.75], ['ion', 0.5, 0.5, 0.5], ['ion', 0.5, 0.25, 0.25], ['ion', 0.5, 0.25, 0.75], ['ion', 0.5, 0.75, 0.25], ['ion', 0.5, 0.75, 0.75], ['ion', 0.25, 0.5, 0.25], ['ion', 0.25, 0.5, 0.75], ['ion', 0.75, 0.5, 0.25], ['ion', 0.75, 0.5, 0.75], ['ion', 0.25, 0.25, 0.5], ['ion', 0.25, 0.75, 0.5], ['ion', 0.75, 0.25, 0.5], ['ion', 0.75, 0.75, 0.5], ['ion', 0.0, 0.25, 0.25], ['ion', 0.25, 0.0, 0.25], ['ion', 0.25, 0.25, 0.0], ['ion', 0.0, 0.25, 0.75], ['ion', 0.25, 0.0, 0.75], ['ion', 0.25, 0.25, 1.0], ['ion', 0.0, 0.75, 0.25], ['ion', 0.25, 0.75, 0.0], ['ion', 0.25, 1.0, 0.25], ['ion', 0.0, 0.75, 0.75], ['ion', 0.25, 0.75, 1.0], ['ion', 0.25, 1.0, 0.75], ['ion', 0.75, 0.0, 0.25], ['ion', 0.75, 0.25, 0.0], ['ion', 1.0, 0.25, 0.25], ['ion', 0.75, 0.0, 0.75], ['ion', 0.75, 0.25, 1.0], ['ion', 1.0, 0.25, 0.75], ['ion', 0.75, 0.75, 0.0], ['ion', 0.75, 1.0, 0.25], ['ion', 1.0, 0.75, 0.25], ['ion', 0.75, 0.75, 1.0], ['ion', 0.75, 1.0, 0.75], ['ion', 1.0, 0.75, 0.75], ['ion', 0.0, 0.5, 0.5], ['ion', 1.0, 0.5, 0.5], ['ion', 0.5, 0.0, 0.5], ['ion', 0.5, 1.0, 0.5], ['ion', 0.5, 0.5, 0.0], ['ion', 0.5, 0.5, 1.0]]
#res = get_lattice_vectors(a)
#res2 = sorted(res)
#count = 0
#for elem in res2:
#    print(elem, res[elem])
#    count += res[elem]
#print(count)

