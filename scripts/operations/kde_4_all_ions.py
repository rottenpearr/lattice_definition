from scripts.operations.lattice_microoperations import get_lattice_vectors3
from scripts.operations.spectrum_operations import kde_array
from collections import Counter
from scripts.grid_generation.macrocubic_NaCl import write_nacl_xyz_inaccurate

from scripts.operations.testing import xyz_to_normalized_coords

a = xyz_to_normalized_coords("../data/NaCl/NaCl_7x7x7.xyz")
# write_nacl_xyz_inaccurate(N=7, a=5.6402, filename="../data/NaCl/NaCl_7x7x7-inaccurate_v2.xyz", extended=True, inaccuracy=1e-2)
# a = xyz_to_normalized_coords("../data/NaCl/NaCl_7x7x7-inaccurate_v2.xyz")

substance_id = 777  # 7772

res = get_lattice_vectors3(a)

kde_arrays = {}

for ion_key, distances in res.items():
    kde_arr = kde_array(dict(Counter(distances)))
    kde_arrays[ion_key] = kde_arr