import numpy as np
from sklearn.decomposition import TruncatedSVD
from ....tools.normalize import log_cpm, log_scran_pooling


def _mnn(adata, n_svd=100):
    import mnnpy

    if min(adata.X.shape) <= n_svd:
        n_svd = min(adata.X.shape) - 1
    if min(adata.obsm["mode2"].shape) <= n_svd:
        n_svd = min(adata.obsm["mode2"].shape) - 1
    # TODO: also normalize obsm["mode2"]
    X_pca = TruncatedSVD(n_svd).fit_transform(adata.X)
    Y_pca = TruncatedSVD(n_svd).fit_transform(adata.obsm["mode2"])
    (X_corrected, Y_corrected), _, _ = mnnpy.mnn_correct(
        X_pca, Y_pca, var_index=np.arange(n_svd), do_concatenate=False
    )
    adata.obsm["aligned"] = X_corrected
    adata.obsm["mode2_aligned"] = Y_corrected


def mnn_log_cpm(adata, n_svd=100):
    log_cpm(adata)
    log_cpm(adata, obsm="mode2", obs="mode2_obs", var="mode2_var")
    _mnn(adata, n_svd=n_svd)


def mnn_log_scran_pooling(adata, n_svd=100):
    log_scran_pooling(adata)
    log_cpm(adata, obsm="mode2", obs="mode2_obs", var="mode2_var")
    _mnn(adata, n_svd=n_svd)
