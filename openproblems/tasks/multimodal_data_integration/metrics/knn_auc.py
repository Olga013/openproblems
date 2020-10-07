import numpy as np
from sklearn.neighbors import NearestNeighbors
from ....tools.decorators import metric
from sklearn.decomposition import TruncatedSVD


@metric(metric_name="kNN Area Under the Curve", maximize=True)
def knn_auc(adata, proportion_neighbors=0.1, n_svd=100):
    if min(adata.X.shape) <= n_svd:
        n_svd = min(adata.X.shape) - 1
    n_neighbors = int(np.ceil(proportion_neighbors * adata.X.shape[0]))
    X_pca = TruncatedSVD(n_svd).fit_transform(adata.X)
    _, indices_true = (
        NearestNeighbors(n_neighbors=n_neighbors).fit(X_pca).kneighbors(X_pca)
    )
    _, indices_pred = (
        NearestNeighbors(n_neighbors=n_neighbors)
        .fit(adata.obsm["aligned"])
        .kneighbors(adata.obsm["mode2_aligned"])
    )
    neighbors_match = np.zeros(n_neighbors, dtype=int)
    for i in range(adata.shape[0]):
        _, pred_matches, true_matches = np.intersect1d(
            indices_pred[i], indices_true[i], return_indices=True
        )
        neighbors_match_idx = np.maximum(pred_matches, true_matches)
        neighbors_match += np.sum(
            np.arange(n_neighbors) >= neighbors_match_idx[:, None],
            axis=0,
        )

    neighbors_match_curve = neighbors_match / (
        np.arange(1, n_neighbors + 1) * adata.shape[0]
    )
    area_under_curve = np.mean(neighbors_match_curve)
    return area_under_curve
