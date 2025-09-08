from scripts.coordinates_nondimensionalization import normalize_coordinates, shift_coordinates
from scripts.operations.lattice_microoperations import get_lattice_vectors2
from scripts.operations.spectrum_operations import create_all_spectrum_plots, plot_spectra

# a = [["ion",0.000000,0.000000,0.000000],
# ["ion",0.000000,0.000000,2.820100],
# ["ion",0.000000,0.000000,5.640200],
# ["ion",0.000000,2.820100,0.000000],
# ["ion",0.000000,2.820100,2.820100],
# ["ion",0.000000,2.820100,5.640200],
# ["ion",0.000000,5.640200,0.000000],
# ["ion",0.000000,5.640200,2.820100],
# ["ion",0.000000,5.640200,5.640200],
# ["ion",2.820100,0.000000,0.000000],
# ["ion",2.820100,0.000000,2.820100],
# ["ion",2.820100,0.000000,5.640200],
# ["ion",2.820100,2.820100,0.000000],
# ["ion",2.820100,2.820100,2.820100],
# ["ion",2.820100,2.820100,5.640200],
# ["ion",2.820100,5.640200,0.000000],
# ["ion",2.820100,5.640200,2.820100],
# ["ion",2.820100,5.640200,5.640200],
# ["ion",5.640200,0.000000,0.000000],
# ["ion",5.640200,0.000000,2.820100],
# ["ion",5.640200,0.000000,5.640200],
# ["ion",5.640200,2.820100,0.000000],
# ["ion",5.640200,2.820100,2.820100],
# ["ion",5.640200,2.820100,5.640200],
# ["ion",5.640200,5.640200,0.000000],
# ["ion",5.640200,5.640200,2.820100],
# ["ion",5.640200,5.640200,5.640200]]
#
# data_dict = {}
# for i in range(len(a)):
#     data_dict[i + 1] = a[i]
# shifted_data = shift_coordinates(data_dict.values())
# normalized_data = normalize_coordinates(shifted_data)
# print(normalized_data)

a = [['ion', 0.0, 0.0, 0.0], ['ion', 0.0, 0.0, 0.5], ['ion', 0.0, 0.0, 1.0], ['ion', 0.0, 0.5, 0.0], ['ion', 0.0, 0.5, 0.5], ['ion', 0.0, 0.5, 1.0], ['ion', 0.0, 1.0, 0.0], ['ion', 0.0, 1.0, 0.5], ['ion', 0.0, 1.0, 1.0], ['ion', 0.5, 0.0, 0.0], ['ion', 0.5, 0.0, 0.5], ['ion', 0.5, 0.0, 1.0], ['ion', 0.5, 0.5, 0.0], ['ion', 0.5, 0.5, 0.5], ['ion', 0.5, 0.5, 1.0], ['ion', 0.5, 1.0, 0.0], ['ion', 0.5, 1.0, 0.5], ['ion', 0.5, 1.0, 1.0], ['ion', 1.0, 0.0, 0.0], ['ion', 1.0, 0.0, 0.5], ['ion', 1.0, 0.0, 1.0], ['ion', 1.0, 0.5, 0.0], ['ion', 1.0, 0.5, 0.5], ['ion', 1.0, 0.5, 1.0], ['ion', 1.0, 1.0, 0.0], ['ion', 1.0, 1.0, 0.5], ['ion', 1.0, 1.0, 1.0]]
res = get_lattice_vectors2(a)

for id, ion in enumerate(res.keys()):
   ion_coords = [float(elem) for elem in ion.split(";")]
   # print(ion, ion_coords, res[ion])
   plot_spectra(data=res[ion], ion=ion_coords, substance_id=9999, vector_id=id, cmap="plasma", background="#20232a")

create_all_spectrum_plots()
