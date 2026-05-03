import os
import pandas as pd
from collections import Counter

from scripts.operations.testing import xyz_to_normalized_coords_with_noise
from scripts.operations.lattice_microoperations import get_lattice_vectors3
from scripts.operations.spectrum_operations import kde_array


def generate_dataset(xyz_filepath, substance_id, substance_name, total_samples=4000, noise_percent=4):
    base_out_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', 'data', 'csv_kde', substance_name)
    )
    for iteration in range(1, total_samples + 1):
        try:
            noisy_coords = xyz_to_normalized_coords_with_noise(
                xyz_filepath,
                noise_percent=noise_percent,
                seed=iteration
            )
            vectors_dict = get_lattice_vectors3(noisy_coords)
            out_dir = os.path.join(base_out_dir, str(iteration))
            os.makedirs(out_dir, exist_ok=True)
            for ion_key, distances in vectors_dict.items():
                kde_arr = kde_array(dict(Counter(distances)))
                ion_coords_str = ion_key.replace(';', '_')
                filename = f'kde_array_{substance_id}_{ion_coords_str}.csv'
                full_path = os.path.join(out_dir, filename)
                df = pd.DataFrame({'kde_values': kde_arr})
                df.to_csv(full_path, index=False)
            print(f"Итерация {iteration} готова")

        except Exception as e:
            print(f"Ошибка на итерации {iteration}: {e}")


if __name__ == "__main__":
    FILE_PATH = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', 'data', 'materials_xyz', 'U2N3_phase2.xyz')
    )

    generate_dataset(
        xyz_filepath=FILE_PATH,
        substance_id="train",
        substance_name='U2N3_phase2_dataset',
        total_samples=400,
        noise_percent=4
    )
