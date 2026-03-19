# -*- coding: utf-8 -*-
"""
Plot the metrics as a hedgehog graph, where we add at timestamp the new optimized order starting from there.
"""


import os
import json
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt


FOLDEROOTS = "./data/processed/paris_simplified_results/"
RAND_TRIAL_NUMBER = 50
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


def main():
    with open("./scripts/05_plot_params_hedgehog.json", "r") as f:
        plot_params = json.load(f)
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    folderplot = FOLDEROOTS+ "plots/lineplot"
    if not os.path.exists(folderplot):
        os.makedirs(folderplot)
    for t in TIMESTAMPS:
        foldertime = FOLDEROOTS + t + "/"
        avg = {}
        for met in plot_params["order"]:
            foldermet = foldertime + met
            if met!= "real":
                foldermet+= "_additive_connected"
                if t != "No":
                    foldermet += "_built"
            foldermet += "/"
            if met == "random":
                df_concat = pd.DataFrame()
                for i in range(RAND_TRIAL_NUMBER):
                    df = pd.read_json(foldermet + f"metrics_growth_{i:02}.json")
                    df_concat = pd.concat([df_concat, df])
            else:
                df_concat = pd.read_json(foldermet + "metrics_growth.json")
            avg[met] = pd.DataFrame(average_x(df_concat))
        for auc in ["AUC of Coverage", "AUC of Directness"]:
            fig, ax = plt.subplots(figsize=plot_params["figsize"])
            if auc == "AUC of Coverage":
                yy = "coverage"
                ax.set_ylabel("Coverage ($km^2$)")
                ratio = 10**6
            else:
                yy = "directness"
                ax.set_ylabel("Directness")
                ratio = 1
            for ids, met in enumerate(plot_params["order"][:7]):
                df = avg[met]
                ax.plot(
                    df["xx"] / 10**3,
                    df[yy] / ratio,
                    **{
                        key: val[ids]
                        for key, val in plot_params.items()
                        if key not in ["dpi", "figsize", "rcparams", "order"]
                    },
                )
            ax.set_xlabel("Built length ($km$)")
            ax.set_axisbelow(True)
            plt.tight_layout()
            plt.legend()
            plt.savefig(folderplot + f"/{t}_{yy}_lineplot_additive_average.png")
            plt.close()


def average_x(df):
    arr = []
    for ind in set(df.index):
        arr.append(df[df.index == ind].mean())
    return arr


if __name__ == "__main__":
    main()