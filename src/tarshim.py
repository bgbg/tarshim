import base64
import io
from typing import Union, IO

import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import seaborn as sns


def _actual_plot_observed_vs_predicted(observations, predictions, ax=None, ylabel=True):
    if ax is None:
        fig, ax = plt.subplots()
    sns.regplot(predictions, observations, ax=ax, ci=99, color='C0')
    mn = min((min(observations), min(predictions)))
    mx = max((max(observations), max(predictions)))

    # Equal aspect ratio
    #     ax.set_aspect(1.0)
    # Identity line for better visual aid
    ax.plot([mn, mx], [mn, mx], '--', color='k', zorder=-1)
    # Equal axis limits
    ax.set_xlim(mn, mx);
    ax.set_ylim(mn, mx)
    sns.despine(ax=ax)
    ax.set_xlabel('Predicted')
    if ylabel:
        ax.set_ylabel('Observed', rotation=0, y=1, va='top', ha='right')
    return ax


def plot_residuals(observations, predictions, ax=None, ylabel=True):
    if ax is None:
        fig, ax = plt.subplots()
    residuals = observations - predictions
    ax.plot(predictions, residuals, 'o', color='C0')
    sns.despine(ax=ax)
    ax.axhline(0, color='k', zorder=-1, ls='--')
    ax.set_xlabel('Predicted', y=-1)
    if ylabel:
        ax.set_ylabel('Obs $-$ Pred', rotation=0, y=1, va='top', ha='right')
    ax.text(x=ax.get_xlim()[1], y=ax.get_ylim()[1], s='Overestimation', color='gray', size='small', ha='right',
            va='top')
    ax.text(x=ax.get_xlim()[1], y=ax.get_ylim()[0], s='Underestimation', color='gray', size='small', ha='right',
            va='bottom')
    return ax


def plot_residual_kde(residuals, ax):
    residuals = residuals.reshape(-1)
    sns.kdeplot(residuals, vertical=True, ax=ax)
    sns.despine(ax=ax, left=True)
    ax.spines['bottom'].set_position('zero')
    ps = np.percentile(residuals, [5, 25, 75, 95]).tolist()
    ps.append(np.mean(residuals))
    tks = np.round(ps, 1)
    secax = ax.secondary_yaxis('right')
    secax.set_yticks(tks)
    ax.set_yticks([0])
    ax.set_yticklabels([0])
    ax.set_xticks([])
    ax.set_xlim(reversed(ax.get_xlim()))
    return ax


def plot_observed_vs_predicted(observations, predictions, fig=None):
    if fig is None:
        fig = plt.figure(figsize=(9, 9 + 3))
    ax_obs_pred = plt.subplot2grid((3, 4), (0, 1), rowspan=2, colspan=3)
    ax_residuals = plt.subplot2grid((3, 4), (2, 1), colspan=3, sharex=ax_obs_pred)
    ax_residual_kde = plt.subplot2grid((3, 4), (2, 0), sharey=ax_residuals)

    _actual_plot_observed_vs_predicted(observations, predictions, ax=ax_obs_pred)
    plot_residuals(observations, predictions, ax=ax_residuals)
    plot_residual_kde(residuals=observations - predictions, ax=ax_residual_kde)
    ax_residual_kde.set_zorder(-1)
    fig.tight_layout()
    fig.subplots_adjust(hspace=0)
    return fig


def savefig(fig: plt.Figure, figfile: Union[str, IO], verbose=False):
    fig.savefig(figfile, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    if verbose:
        print(f'Saved {figfile}')


def cell_figure_mapping(fig):
    figfile = io.BytesIO()
    fig.savefig(figfile, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue()).decode()
    imgstr = '<img src="data:image/png;base64,{}" />'.format(figdata_png)
    return imgstr


def html_from_dataframe(df: pd.DataFrame, figure_columns=None) -> str:
    if hasattr(df, 'render'):
        return df.render()
    if figure_columns is None:
        figure_columns = []
    elif figure_columns == 'infer':
        figure_columns = [c for c in df.columns if c[1] == 'fig']
    else:
        for c in figure_columns:
            assert c in df.columns
    formatters = {c: cell_figure_mapping for c in figure_columns}
    df = df.copy()
    ret = df.to_html(escape=False, formatters=formatters, border=0)
    return ret


def arrowed_spines(
        ax=None,
        color='k', markersize=10,
):
    if ax is None:
        ax = plt.gca()
    ax.plot(1, 0, ls="", marker=">", ms=markersize, color=color,
            transform=ax.transAxes, clip_on=False)
    ax.plot(0, 1, ls="", marker="^", ms=markersize, color=color,
            transform=ax.transAxes, clip_on=False)
    return ax

def despine(full=False, **kwargs):
    if full:
        if 'ax' in kwargs:
            ax = kwargs['ax']
        else:
            ax = plt.gca()
        ax.set_xticks([])
        ax.set_yticks([])
        for w in ['left', 'right', 'top', 'bottom']:
            kwargs[w] = True
    ret = sns.despine(**kwargs)
    return ret


def cleanup(ax=None, do_despine=True, add_arrows=True, remove_ticks=False):
    if ax is None:
        ax = plt.gca()
    if add_arrows:
        arrowed_spines(ax=ax)
    if remove_ticks:
        ax.set_yticks([])
        ax.set_xticks([])
    if do_despine:
        despine(ax=ax)
    return ax
