import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns


def make_sample_data(n_points=10, seed=None, noise=1.0):
    if seed is not None:
        np.random.seed(seed)
    x = np.linspace(-10, 10, n_points)
    degree = np.random.randint(1, 6)
    p = np.random.randn(degree + 1)
    y = np.polyval(p, x) + np.random.randn(n_points) * noise
    return p, x, y


def plot_summary(x, y_obs, y_pred):
    fig, axes = plt.subplots(ncols=2)
    ax = axes[0]
    ax.plot(x, y_obs, "-")
    ax.plot(x, y_pred, "o", mec="C1", mfc="none")
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    ax = axes[1]
    ax.set_aspect(1.0)
    mn = min([min(x), min(y_obs), min(y_pred)])
    mx = max([max(x), max(y_obs), max(y_pred)])
    ax.plot([mn, mx], [mn, mx], "k--")
    ax.plot(y_pred, y_obs, "o", mec="k", mfc="none")
    ax.set_xlabel("Prediction")
    ax.set_ylabel("Observation", rotation=0, ha="left", va="bottom", y=1)
    for ax in axes:
        sns.despine(ax=ax)
    return fig, axes


def aic(y_obs, y_pred, n_params: int) -> float:
    """Akaike information criterion."""
    n = len(y_obs)
    sse = np.sum((y_obs - y_pred) ** 2)
    aic = n * np.log(sse / n) + 2 * n_params
    return aic
