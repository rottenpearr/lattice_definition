from pymatgen.core import Structure
from sklearn.preprocessing import StandardScaler
import pandas as pd
import hdbscan
import matplotlib.pyplot as plt
import umap.umap_ as umap


def extract_features_from_cif(cif_path):
    struct = Structure.from_file(cif_path)
    return {
        'a': struct.lattice.a,
        'b': struct.lattice.b,
        'c': struct.lattice.c,
        'alpha': struct.lattice.alpha,
        'beta': struct.lattice.beta,
        'gamma': struct.lattice.gamma,
        'volume': struct.volume,
        'num_sites': len(struct.sites),
    }


def cluster_structures(cif_paths, min_cluster_size=2):
    records = []
    for path in cif_paths:
        try:
            f = extract_features_from_cif(path)
            f['file'] = path
            records.append(f)
        except Exception:
            pass

    df = pd.DataFrame(records)
    X = StandardScaler().fit_transform(df.drop(columns=['file'], errors='ignore'))

    labels = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=1,
        metric='euclidean',
        cluster_selection_method='eom',
    ).fit_predict(X)

    df['cluster'] = labels
    return df, X, labels


def plot_umap(df, X, labels):
    reducer = umap.UMAP(
        n_components=2,
        random_state=42,
        n_neighbors=min(5, len(X) - 1),
    )
    embedding = reducer.fit_transform(X)

    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(embedding[:, 0], embedding[:, 1], c=labels, cmap='Spectral', s=100, alpha=0.7)
    for i, txt in enumerate(df['file']):
        plt.annotate(str(txt).split('/')[-1].split('.')[0], (embedding[i, 0], embedding[i, 1]), fontsize=8)
    plt.colorbar(scatter, label='HDBSCAN cluster')
    plt.grid(True)
    plt.show()
