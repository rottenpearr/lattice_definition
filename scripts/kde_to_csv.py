import pandas as pd
from operations.kde_4_all_ions import kde_arrays, substance_id
from os.path import normpath, join, dirname

path_to_db = normpath(join(dirname(__file__), '..', 'data', 'csv_kde', '7x7x7'))
print(path_to_db)

# Сохраняем KDE для каждого иона в отдельный файл
for ion_key, kde_arr in kde_arrays.items():
    df = pd.DataFrame({'kde_values': kde_arr})
    # Создаем имя файла с координатами иона
    ion_coords = ion_key.replace(';', '_')
    filename = f'kde_array_{substance_id}_{ion_coords}.csv'
    full_path = join(path_to_db, filename)
    df.to_csv(full_path, index=False)
    print(f"Сохранен KDE для иона {ion_key} в файл {filename}")

print(f"Всего сохранено {len(kde_arrays)} KDE массивов")