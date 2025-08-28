def shift_coordinates(data):
    min_x = min(point[1] for point in data)
    min_y = min(point[2] for point in data)
    min_z = min(point[3] for point in data)
    shift_vector = [-min_x, -min_y, -min_z]  # Вектор сдвига
    shifted_data = [
        [point[0], point[1] + shift_vector[0], point[2] + shift_vector[1], point[3] + shift_vector[2]]
        for point in data
    ]
    return shifted_data


def normalize_coordinates(shifted_data):
    max_coordinate = max(
        max(point[1:]) for point in shifted_data
    )
    if max_coordinate == 0:
        raise ValueError("Максимальная координата равна 0. Нормализация невозможна.")
    normalized_data = [
        [point[0]] + [coord / max_coordinate for coord in point[1:]]
        for point in shifted_data
    ]
    return normalized_data
