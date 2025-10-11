from scripts.operations.lattice_microoperations import get_lattice_vectors3
from scripts.operations.spectrum_operations import kde_array
from collections import Counter
from os.path import normpath, join, dirname

from scripts.operations.testing import xyz_to_normalized_coords

path_to_xyz = normpath(join(dirname(__file__), '..', '..', 'data', 'xyz', '1523015_UN2.xyz'))
a = xyz_to_normalized_coords(path_to_xyz)

substance_id = 777

res = get_lattice_vectors3(a)

kde_arrays = {}

for ion_key, distances in res.items():
    kde_arr = kde_array(dict(Counter(distances)))
    kde_arrays[ion_key] = kde_arr