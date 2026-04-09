# -*- coding: utf-8 -*-
"""
Plot subtractive values for 2021, for script 2, 3, and 6.
"""

import json
import os
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import osmnx as ox
from orderbike.plot import plot_growth
from orderbike.utils import auc_from_metrics_dict

FOLDEROOTS = "../data/processed/paris_simplified_results/"
FILENAME = "paris_cleaned_multigraph.graphml"
TIMESTAMPS = [
    "2021-01-01",
    "2023-05-17",
    "2023-10-01",
    "2024-01-15",
    "2024-04-04",
    "2024-08-22",
    "2024-12-22",
    "2025-06-02",
    "No",
]
RAND_TRIAL_NUMBER = 50
BUFF_SIZE = 400
BUFFER = True
PLOT_METRICS = False
DPI = 100  # Larger means bigger files and longer to save, and there are a lot of pictures so quickly taking space and time
MET_LIST = [
    # "adaptive_coverage",
    # "coverage",
    # "relative_directness",
    # "directness",
    # "betweenness",
    # "closeness",
    "directness_alt"
]


def main():
    for exp_disc in [True, False]:
        timestamp_aucs = []
        foldertime = FOLDEROOTS + "2021-01-01/"
        # Open for all growth strategies for a toy graph
        for metric in [
            "adaptive_coverage",
            "coverage",
            "relative_directness",
            "directness",
            "directness_alt",
            "betweenness",
            "closeness",
            "random",
        ]:
            foldermet = foldertime + metric + "_subtractive_connected_built"
            foldermet += "/"
            if metric == "random":
                for i in range(RAND_TRIAL_NUMBER):
                    with open(foldermet + f"metrics_growth_{i:02}.json", "r") as f:
                        met_dict = json.load(f)
                    auc_cov = auc_from_metrics_dict(
                        met_dict,
                        "coverage",
                        normalize_y=True,
                        yaxis_method="natural",
                        exp_discounting=exp_disc,
                        normalize_max_auc=False,
                    )
                    auc_dir = auc_from_metrics_dict(
                        met_dict,
                        "directness",
                        normalize_y=False,
                        max_comparison_y="one",
                        exp_discounting=exp_disc,
                        normalize_max_auc=False,
                    )
                    auc_dir_alt = auc_from_metrics_dict(
                        met_dict,
                        "directness_alt",
                        normalize_y=False,
                        max_comparison_y="one",
                        exp_discounting=exp_disc,
                        normalize_max_auc=False,
                    )
                    timestamp_aucs.append(
                        ["2021-01-01", metric, i, auc_cov, auc_dir, auc_dir_alt]
                    )
            else:
                with open(foldermet + "metrics_growth.json", "r") as f:
                    met_dict = json.load(f)
                auc_cov = auc_from_metrics_dict(
                    met_dict,
                    "coverage",
                    normalize_y=True,
                    yaxis_method="natural",
                    exp_discounting=exp_disc,
                    normalize_max_auc=False,
                )
                auc_dir = auc_from_metrics_dict(
                    met_dict,
                    "directness",
                    normalize_y=False,
                    max_comparison_y="one",
                    exp_discounting=exp_disc,
                    normalize_max_auc=False,
                )
                auc_dir_alt = auc_from_metrics_dict(
                    met_dict,
                    "directness_alt",
                    normalize_y=False,
                    max_comparison_y="one",
                    exp_discounting=exp_disc,
                    normalize_max_auc=False,
                )
                timestamp_aucs.append(
                    ["2021-01-01", metric, 0, auc_cov, auc_dir, auc_dir_alt]
                )
            # Save everything as JSON with Pandas Dataframe
            df_growth = pd.DataFrame(
                timestamp_aucs,
                columns=[
                    "Timestamp",
                    "Metric optimized",
                    "Trial",
                    "AUC of Coverage",
                    "AUC of Directness",
                    "AUC of Directness (alt)",
                ],
            )
            savename = str(FOLDEROOTS) + "auc_table_growth_subtractive"
            if exp_disc:
                savename += "_expdisc"
            savename += ".json"
            df_growth.to_json(savename)
    with open("../scripts/03_plot_params_AUC.json", "r") as f:
        plot_params = json.load(f)
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    folderplot = FOLDEROOTS + "plots/AUC"
    if not os.path.exists(folderplot):
        os.makedirs(folderplot)
    for exp in [True, False]:
        for x_choice in ["AUC of Directness", "AUC of Directness (alt)"]:
            savename = str(FOLDEROOTS) + "/auc_table_growth_subtractive"
            if exp:
                savename += "_expdisc"
            savename += ".json"
            df_growth = pd.read_json(savename)
            fig, ax = plt.subplots(figsize=plot_params["figsize"])
            for ids, met in enumerate(plot_params["order"]):
                mask_met = df_growth["Metric optimized"] == met
                ax.scatter(
                    df_growth[mask_met][x_choice],
                    df_growth[mask_met]["AUC of Coverage"],
                    zorder=2,
                    **{
                        key: val[ids]
                        for key, val in plot_params.items()
                        if key
                        not in [
                            "dpi",
                            "figsize",
                            "rcparams",
                            "order",
                            "errorbar",
                        ]
                    },
                )
                if met == "random":
                    xx_mean = df_growth[mask_met][x_choice].mean()
                    xx_std = df_growth[mask_met][x_choice].std()
                    yy_mean = df_growth[mask_met]["AUC of Coverage"].mean()
                    yy_std = df_growth[mask_met]["AUC of Coverage"].std()
                    ax.errorbar(
                        x=xx_mean,
                        y=yy_mean,
                        yerr=yy_std * 2,
                        xerr=xx_std * 2,
                        fmt="o",
                        **{key: val for key, val in plot_params["errorbar"].items()},
                    )
            ax.set_xlabel(x_choice)
            ax.set_ylabel("AUC of coverage")
            savename = folderplot + "/AUC_comparison_cov_dir"
            if x_choice == "AUC of Directness (alt)":
                savename += "_alt"
            savename += "_2021-01-01_subtractive"
            if exp:
                savename += "_expdisc"
            # Put ticks at each 0.1
            loc = mpl.ticker.MultipleLocator(base=0.1)
            ax.xaxis.set_major_locator(loc)
            ax.yaxis.set_major_locator(loc)
            plt.axis("square")
            # Set rounded limits at smallest and highest 0.1
            dirmin = df_growth[x_choice].min()
            dirmax = df_growth[x_choice].max()
            covmin = df_growth["AUC of Coverage"].min()
            covmax = df_growth["AUC of Coverage"].max()
            mmin = round(min(dirmin, covmin) - 0.05, 1)
            mmax = round(max(dirmax, covmax) + 0.05, 1)
            ax.set_xlim([mmin, mmax])
            ax.set_ylim([mmin, mmax])
            parfront = df_growth.copy()
            parfront = parfront[
                parfront.apply(
                    lambda x: is_pareto_efficient(
                        x, parfront, "AUC of Coverage", x_choice
                    ),
                    axis=1,
                )
            ]
            parfront.sort_values(x_choice, axis=0, inplace=True)
            ax.plot(
                parfront[x_choice],
                parfront["AUC of Coverage"],
                linestyle="dashed",
                linewidth=1,
                color="black",
                zorder=1,
                label="Pareto front",
            )
            plt.legend(prop={"size": plot_params["rcparams"]["font.size"] * 0.75})
            plt.savefig(savename)
            plt.close()
    G = ox.load_graphml(FOLDEROOTS + "/" + FILENAME)
    folderplot = FOLDEROOTS + "plots/growths/"
    if not os.path.exists(folderplot):
        os.makedirs(folderplot)
    H = G.copy()
    built = True
    for e in H.edges:
        if H.edges[e]["built"] == "2021-01-01":
            H.edges[e]["built"] = 1
        else:
            H.edges[e]["built"] = 0
    foldertime = FOLDEROOTS + "2021-01-01/"
    foldertimeplot = folderplot + "2021-01-01_subtractive/"
    if not os.path.exists(foldertimeplot):
        os.makedirs(foldertimeplot)
    for met in MET_LIST:
        foldermet = foldertime + met + "_subtractive_connected_built"
        foldermet += "/"
        foldermetplot = foldertimeplot + met + "/"
        if not os.path.exists(foldermetplot):
            os.makedirs(foldermetplot)
        with open(foldermet + "order_growth.json") as f:
            order_growth = json.load(f)
        order_growth = [tuple(val) for val in order_growth]
        with open(foldermet + "metrics_growth.json") as f:
            metrics_dict = json.load(f)
        plot_growth(
            H,
            order_growth,
            foldermetplot,
            built=built,
            color_built="firebrick",
            color_added="steelblue",
            color_newest="darkgreen",
            node_size=8,
            buffer=BUFFER,
            buff_size=BUFF_SIZE,
            plot_metrics=PLOT_METRICS,
            growth_cov=metrics_dict["coverage"],
            growth_xx=metrics_dict["xx"],
            growth_dir=metrics_dict["directness"],
            growth_reldir=metrics_dict["relative_directness"],
            dpi=DPI,
        )


def is_pareto_efficient(x, df, fdim, sdim):
    return ~np.any(df[(df[fdim] > x[fdim]) & (df[sdim] > x[sdim])])


def average_x(df):
    arr = []
    for ind in set(df.index):
        arr.append(df[df.index == ind].mean())
    return arr


if __name__ == "__main__":
    main()
