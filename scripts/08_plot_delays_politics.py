# -*- coding: utf-8 -*-
"""
Plot political plots.
"""

import json
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import geopandas as gpd

FOLDEROOTS = "./data/processed/paris_simplified_results/"
BINS_ARR = 4


# TODO separate into two different scripts?
def main():
    folderplot = FOLDEROOTS + "plots/votes/"
    if not os.path.exists(folderplot):
        os.makedirs(folderplot)
    with open("./scripts/08_plot_delays_politics.json", "r") as f:
        plot_params = json.load(f)
    gdf_vote = gpd.read_file(FOLDEROOTS + "paris_vote_arr_bikenet.gpkg")
    # Plot map
    fig, ax = plt.subplots(figsize=plot_params["figsize"], layout="constrained")
    ax.axis("off")
    gdf_vote.plot(
        ax=ax,
        column="length_accomplished_share",
        **{key: val for key, val in plot_params.items() if key in ["cmap", "scheme"]},
        legend=True,
    )
    fig.savefig(folderplot + "map_delays_vote_arr.png")
    # Plot probability of lanes built by share of vote
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    bin_edges = np.linspace(
        min(gdf_vote[["LUG_share", "LUD_share"]].min()),
        max(gdf_vote[["LUG_share", "LUD_share"]].max()),
        num=BINS_ARR + 1,
    )
    mean_acc = gdf_vote["length_accomplished_share"].mean()
    for center in [True, False]:
        fig, ax = plt.subplots(figsize=plot_params["figsize"])
        for ids in range(len(plot_params["party"])):
            res = [
                gdf_vote[
                    (gdf_vote[plot_params["party"][ids]] >= bin_edges[i])
                    & (gdf_vote[plot_params["party"][ids]] < bin_edges[i + 1])
                ]["length_accomplished_share"].mean()
                for i in range(len(bin_edges) - 1)
            ]
            if center:
                res = res - mean_acc
            err = [
                gdf_vote[
                    (gdf_vote[plot_params["party"][ids]] >= bin_edges[i])
                    & (gdf_vote[plot_params["party"][ids]] < bin_edges[i + 1])
                ]["length_accomplished_share"].sem()
                for i in range(len(bin_edges) - 1)
            ]
            ax.errorbar(
                [
                    (bin_edges[i] + bin_edges[i + 1]) / 2
                    for i in range(len(bin_edges) - 1)
                ],
                res,
                yerr=err,
                **{
                    key: val[ids]
                    for key, val in plot_params.items()
                    if key not in ["figsize", "rcparams", "party", "cmap", "scheme"]
                },
            )
        if center:
            yy = [0, 0]
        else:
            yy = [mean_acc, mean_acc]
        ax.plot(
            [bin_edges[0], bin_edges[-1]],
            yy,
            linestyle="dashed",
            color="#E1E1E1",
            zorder=0,
            label="Average accomplishment",
        )
        # TODO add legend modification
        ax.legend()
        ax.set_xlabel("Share of votes for the party")
        ylabel = "Share of bicycle lanes accomplished"
        if center:
            ylabel += ", centered"
        ax.set_ylabel(ylabel)
        ax.set_xlim([0.05, 0.75])
        ylim = [-0.3, 0.3]
        if not center:
            ylim += mean_acc
        ax.set_ylim(ylim)
        filename = "probability_delays_vote_arr_sem"
        if center:
            filename += "_centered"
        fig.savefig(folderplot + filename + ".png")


if __name__ == "__main__":
    main()
