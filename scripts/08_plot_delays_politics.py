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
import statsmodels.api as sm

FOLDEROOTS = "./data/processed/paris_simplified_results/"
BINS_ARR = 4


# TODO separate into two different scripts?
def main():
    folderplot = FOLDEROOTS + "plots/votes/"
    if not os.path.exists(folderplot):
        os.makedirs(folderplot)
    with open("./scripts/08_plot_delays_politics.json", "r") as f:
        plot_params = json.load(f)
    gdf_vote = gpd.read_file(FOLDEROOTS + "paris_vote_arr_2020_bikenet.gpkg")
    # Plot map
    fig, ax = plt.subplots(figsize=plot_params["figsize"], layout="constrained")
    ax.axis("off")
    gdf_vote.plot(
        ax=ax,
        column="length_accomplished_share",
        **{key: val for key, val in plot_params.items() if key in ["cmap", "scheme"]},
        legend=True,
    )
    fig.savefig(folderplot + "map_delays_vote_2020_arr.png")
    # Plot probability of lanes built by share of vote
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    mean_acc = gdf_vote["length_accomplished_share"].mean()
    bin_edges = np.linspace(
        min(gdf_vote[["Left_wing_share", "Right_wing_share"]].min()),
        max(gdf_vote[["Left_wing_share", "Right_wing_share"]].max()),
        num=BINS_ARR + 1,
    )
    fig, ax = plt.subplots(figsize=plot_params["figsize"])
    for ids in range(len(plot_params["party"])):
        res = [
            gdf_vote[
                (gdf_vote[plot_params["party"][ids]] >= bin_edges[i])
                & (gdf_vote[plot_params["party"][ids]] < bin_edges[i + 1])
            ]["length_accomplished_share"].mean()
            for i in range(len(bin_edges) - 1)
        ]
        err = [
            gdf_vote[
                (gdf_vote[plot_params["party"][ids]] >= bin_edges[i])
                & (gdf_vote[plot_params["party"][ids]] < bin_edges[i + 1])
            ]["length_accomplished_share"].sem()
            for i in range(len(bin_edges) - 1)
        ]
        ax.errorbar(
            [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(len(bin_edges) - 1)],
            res,
            yerr=err,
            **{
                key: val[ids]
                for key, val in plot_params.items()
                if key not in ["figsize", "rcparams", "party", "cmap", "scheme"]
            },
        )
    ax.plot(
        [bin_edges[0], bin_edges[-1]],
        [mean_acc, mean_acc],
        linestyle="dashed",
        color="#E1E1E1",
        zorder=0,
        label="Average accomplishment",
    )
    # TODO add legend modification
    ax.legend()
    ax.set_xlabel("Share of votes")
    ax.set_ylabel("Share of bicycle lanes accomplished")
    ax.set_xlim([0.05, 0.75])
    filename = "probability_delays_vote_arr_2020_sem"
    fig.savefig(folderplot + filename + ".png")
    bin_edges = np.linspace(
        gdf_vote["ratio_LR"].min(),
        gdf_vote["ratio_LR"].max(),
        num=BINS_ARR + 2,
    )
    fig, ax = plt.subplots(figsize=plot_params["figsize"])
    res = [
        gdf_vote[
            (gdf_vote["ratio_LR"] >= bin_edges[i])
            & (gdf_vote["ratio_LR"] < bin_edges[i + 1])
        ]["length_accomplished_share"].mean()
        for i in range(len(bin_edges) - 1)
    ]
    err = [
        gdf_vote[
            (gdf_vote["ratio_LR"] >= bin_edges[i])
            & (gdf_vote["ratio_LR"] < bin_edges[i + 1])
        ]["length_accomplished_share"].sem()
        for i in range(len(bin_edges) - 1)
    ]
    ax.errorbar(
        [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(len(bin_edges) - 1)],
        res,
        yerr=err,
        **{
            key: val[-1]
            for key, val in plot_params.items()
            if key not in ["figsize", "rcparams", "party", "cmap", "scheme", "legend"]
        },
    )
    ax.plot(
        [bin_edges[0], bin_edges[-1]],
        [mean_acc, mean_acc],
        linestyle="dashed",
        color="#E1E1E1",
        zorder=0,
        label="Average accomplishment",
    )
    ax.set_xlabel("Left/Right vote share anomaly")
    ax.set_ylabel("Share of bicycle lanes accomplished")
    ax.set_xlim([-0.35, 0.55])
    filename = "probability_delays_vote_arr_fused_2020_sem"
    fig.savefig(folderplot + filename + ".png")
    model = sm.OLS(
        gdf_vote["length_accomplished_share"],
        sm.add_constant(gdf_vote["ratio_LR"].values),
    ).fit()
    fig, ax = plt.subplots(figsize=plot_params["figsize"])
    ax.scatter(
        gdf_vote["ratio_LR"],
        gdf_vote["length_accomplished_share"],
        s=40,
        **{
            key: val[-1]
            for key, val in plot_params.items()
            if key
            not in [
                "figsize",
                "rcparams",
                "party",
                "cmap",
                "scheme",
                "label",
                "markersize",
            ]
        },
        label="Arrondissements",
    )
    ax.plot(
        [-0.5, 1],
        [mean_acc, mean_acc],
        linestyle="dashed",
        color="#E1E1E1",
        zorder=0,
        label="Expected value",
    )
    ax.plot(
        [0, 0],
        [0, 1],
        linestyle="dashed",
        color="#E1E1E1",
        zorder=0,
    )
    xx = np.linspace(
        gdf_vote["ratio_LR"].min() - 0.05, gdf_vote["ratio_LR"].max() + 0.05, num=100
    )
    ax.plot(
        xx,
        model.params["x1"] * xx + model.params["const"],
        color="#000000",
        label="Linear regression",
        linewidth=2,
    )
    ax.set_ylabel("Share of bicycle lanes accomplished")
    ax.set_xlabel("Left/Right vote share anomaly")
    ax.set_xlim([-0.5, 1])
    ax.set_ylim([0, 1])
    ax.legend()
    filename = "scatterplot_delays_vote_arr_fused_2020"
    fig.savefig(folderplot + filename + ".png")


if __name__ == "__main__":
    main()
