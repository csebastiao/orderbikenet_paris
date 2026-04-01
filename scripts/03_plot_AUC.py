# -*- coding: utf-8 -*-
"""
Plot the AUC in additive order of all strategies on the tested graphs.
"""

import os
import json
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np


FOLDEROOTS = "./data/processed/paris_simplified_results/"
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
X_CHOICE = "AUC of Directness"


def main():
    with open("./scripts/03_plot_params_AUC.json", "r") as f:
        plot_params = json.load(f)
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    folderplot = FOLDEROOTS + "plots/AUC"
    if not os.path.exists(folderplot):
        os.makedirs(folderplot)
    for exp in [True, False]:
        savename = str(FOLDEROOTS) + "/auc_table_growth_additive"
        if exp:
            savename += "_expdisc"
        savename += ".json"
        df_growth = pd.read_json(savename)
        for t in TIMESTAMPS:
            mask_tim = df_growth["Timestamp"] == t
            if t != "No":
                size = 8
            else:
                size = 9
            fig, ax = plt.subplots(figsize=plot_params["figsize"])
            for ids, met in enumerate(plot_params["order"][:size]):
                mask_met = df_growth["Metric optimized"] == met
                ax.scatter(
                    df_growth[mask_tim & mask_met][X_CHOICE],
                    df_growth[mask_tim & mask_met]["AUC of Coverage"],
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
                    xx_mean = df_growth[mask_tim & mask_met][X_CHOICE].mean()
                    xx_std = df_growth[mask_tim & mask_met][X_CHOICE].std()
                    yy_mean = df_growth[mask_tim & mask_met]["AUC of Coverage"].mean()
                    yy_std = df_growth[mask_tim & mask_met]["AUC of Coverage"].std()
                    ax.errorbar(
                        x=xx_mean,
                        y=yy_mean,
                        yerr=yy_std * 2,
                        xerr=xx_std * 2,
                        fmt="o",
                        **{key: val for key, val in plot_params["errorbar"].items()},
                    )
            ax.set_xlabel(X_CHOICE)
            ax.set_ylabel("AUC of coverage")
            savename = folderplot + f"/AUC_comparison_cov_dir_{t}"
            if exp:
                savename += "_expdisc"
            # Put ticks at each 0.1
            loc = mpl.ticker.MultipleLocator(base=0.1)
            ax.xaxis.set_major_locator(loc)
            ax.yaxis.set_major_locator(loc)
            plt.axis("square")
            # Set rounded limits at smallest and highest 0.1
            dirmin = df_growth[mask_tim][X_CHOICE].min()
            dirmax = df_growth[mask_tim][X_CHOICE].max()
            covmin = df_growth[mask_tim]["AUC of Coverage"].min()
            covmax = df_growth[mask_tim]["AUC of Coverage"].max()
            mmin = round(min(dirmin, covmin) - 0.05, 1)
            mmax = round(max(dirmax, covmax) + 0.05, 1)
            ax.set_xlim([mmin, mmax])
            ax.set_ylim([mmin, mmax])
            parfront = df_growth[mask_tim].copy()
            parfront = parfront[
                parfront.apply(
                    lambda x: is_pareto_efficient(
                        x, parfront, "AUC of Coverage", X_CHOICE
                    ),
                    axis=1,
                )
            ]
            parfront.sort_values(X_CHOICE, axis=0, inplace=True)
            ax.plot(
                parfront[X_CHOICE],
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


def is_pareto_efficient(x, df, fdim, sdim):
    return ~np.any(df[(df[fdim] > x[fdim]) & (df[sdim] > x[sdim])])


def average_x(df):
    arr = []
    for ind in set(df.index):
        arr.append(df[df.index == ind].mean())
    return arr


if __name__ == "__main__":
    main()
