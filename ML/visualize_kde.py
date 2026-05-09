import pandas as pd
import matplotlib.pyplot as plt
from os.path import normpath, join, dirname

data = pd.read_csv(normpath(join(dirname(__file__), '..', 'data', 'csv_kde', 'NaCl_3x3x3_norm', '1', 'kde_array_777_Cl_0.00000000_0.00000000_0.00000000.csv')),
                   header=None, skiprows=1)

plt.plot(data.values.flatten())
plt.grid(True)
plt.show()