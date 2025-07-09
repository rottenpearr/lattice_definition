from os.path import dirname, join, normpath, basename
from pymatgen.core import Structure
from sklearn.preprocessing import StandardScaler
import pandas as pd
import hdbscan
import matplotlib.pyplot as plt
import umap.umap_ as umap

path_to_cif11 = normpath(
    join(dirname(''), '..', 'data', 'cif', 'cubic', 'гранецентрированные Fm-3m (225)', '1000041.cif'))
path_to_cif12 = normpath(
    join(dirname(''), '..', 'data', 'cif', 'cubic', 'гранецентрированные Fm-3m (225)', '1000044.cif'))
path_to_cif13 = normpath(
    join(dirname(''), '..', 'data', 'cif', 'cubic', 'гранецентрированные Fm-3m (225)', '1000053.cif'))
path_to_cif14 = normpath(
    join(dirname(''), '..', 'data', 'cif', 'cubic', 'гранецентрированные Fm-3m (225)', '1010387.cif'))
path_to_cif15 = normpath(
    join(dirname(''), '..', 'data', 'cif', 'cubic', 'гранецентрированные Fm-3m (225)', '1010876.cif'))

path_to_cif21 = normpath(
    join(dirname(''), '..', 'data', 'cif', 'cubic', 'простые Pm-3m (221)', '1000050.cif'))
path_to_cif22 = normpath(
    join(dirname(''), '..', 'data', 'cif', 'cubic', 'простые Pm-3m (221)', '1001775.cif'))
path_to_cif23 = normpath(
    join(dirname(''), '..', 'data', 'cif', 'cubic', 'простые Pm-3m (221)', '1010167.cif'))
path_to_cif24 = normpath(
    join(dirname(''), '..', 'data', 'cif', 'cubic', 'простые Pm-3m (221)', '1010302.cif'))


def extract_features_from_cif(cif_path):
    try:
        struct = Structure.from_file(cif_path)
        features = {
            'a': struct.lattice.a,
            'b': struct.lattice.b,
            'c': struct.lattice.c,
            'alpha': struct.lattice.alpha,
            'beta': struct.lattice.beta,
            'gamma': struct.lattice.gamma,
            'volume': struct.volume,
            'num_sites': len(struct.sites)
        }
        return features
    except Exception as e:
        return e

cif_files = [path_to_cif11, path_to_cif12, path_to_cif13, path_to_cif14, path_to_cif15,
             path_to_cif21, path_to_cif22, path_to_cif23, path_to_cif24]
features_cif = []

# отдельный метод
for cif_file in cif_files:
    features = extract_features_from_cif(cif_file)
    if features: # если какой-то .cif не прочтётся, то и не попадет в датафрейм
        features['file'] = basename(cif_file)
        features_cif.append(features)
df = pd.DataFrame(features_cif)
features = df.drop(columns=['file', 'name'], errors='ignore')
X_scaled = StandardScaler().fit_transform(features)

# отдельно кластеризацию
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=2,
    min_samples=1,
    metric='euclidean',
    cluster_selection_method='eom'
)
labels = clusterer.fit_predict(X_scaled)
df['cluster'] = labels

# UMAP чтобы понизить размерность и посмотреть в 2D (отдельно)
reducer = umap.UMAP(
    n_components=2,  # 2D
    random_state=42,
    n_neighbors=min(5, len(X_scaled)-1)
)
embedding = reducer.fit_transform(X_scaled)

# Визуализация
plt.figure(figsize=(10, 8))
scatter = plt.scatter(
    embedding[:, 0],
    embedding[:, 1],
    c=labels,
    cmap='Spectral',
    s=100,
    alpha=0.7
)

for i, txt in enumerate(df['file']):
    plt.annotate(txt.split('.')[0], (embedding[i, 0], embedding[i, 1]), fontsize=8)

plt.colorbar(scatter, label='Кластеринг с HDBSCAN')
plt.grid(True)
plt.show()