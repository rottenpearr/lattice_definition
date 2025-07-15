#import sys
import numpy as np
from pathlib import Path

from db.coordinates_nondimensionalization import shift_coordinates, normalize_coordinates
from db.xyz_to_db import parse_xyz


def get_vectors(atoms):
    # Преобразуем координаты и названия отдельно
    elements = [row[0] for row in atoms]
    coords = np.array([row[1:] for row in atoms])  # shape: (n, 3)

    n = len(coords)
    vectors = []

    for i in range(n):
        for j in range(n):
            if i != j:
                vec = coords[j] - coords[i]  # вектор от i к j
                vectors.append((i, j, vec))  # можно также сохранить элементы: (elements[i], elements[j], vec)

    # Пример вывода
    # for i, j, vec in vectors:
    #     print(f"{elements[i]}{i + 1} → {elements[j]}{j + 1}: вектор = {vec}")

    return vectors


try:
    filename = input('Enter filename: ')
    xyz_file_path = Path(f"../data/xyz/{filename}.xyz")
    data = parse_xyz(xyz_file_path)
    shifted_data = shift_coordinates(data)
    normalized_data = normalize_coordinates(shifted_data)

    atoms = normalized_data
    vectors = get_vectors(atoms)

    #for atom in atoms:
    #    print(atom)
except Exception as e:
    print(f"Произошла ошибка: {e}")
