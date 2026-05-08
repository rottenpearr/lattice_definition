from os.path import normpath, join
from cris.core.clustering import cluster_structures, plot_umap

cif_files = [
    normpath(join('..', 'data', 'cif', 'cubic', 'гранецентрированные Fm-3m (225)', '1000041.cif')),
    normpath(join('..', 'data', 'cif', 'cubic', 'гранецентрированные Fm-3m (225)', '1000044.cif')),
    normpath(join('..', 'data', 'cif', 'cubic', 'гранецентрированные Fm-3m (225)', '1000053.cif')),
    normpath(join('..', 'data', 'cif', 'cubic', 'гранецентрированные Fm-3m (225)', '1010387.cif')),
    normpath(join('..', 'data', 'cif', 'cubic', 'гранецентрированные Fm-3m (225)', '1010876.cif')),
    normpath(join('..', 'data', 'cif', 'cubic', 'простые Pm-3m (221)', '1000050.cif')),
    normpath(join('..', 'data', 'cif', 'cubic', 'простые Pm-3m (221)', '1001775.cif')),
    normpath(join('..', 'data', 'cif', 'cubic', 'простые Pm-3m (221)', '1010167.cif')),
    normpath(join('..', 'data', 'cif', 'cubic', 'простые Pm-3m (221)', '1010302.cif')),
]

if __name__ == "__main__":
    df, X, labels = cluster_structures(cif_files)
    plot_umap(df, X, labels)
