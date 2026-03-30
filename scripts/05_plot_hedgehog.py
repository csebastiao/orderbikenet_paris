# -*- coding: utf-8 -*-
"""
Plot the metrics as a hedgehog graph, where we add at timestamp the new optimized order starting from there.
"""


import os
import json
import pandas as pd
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt


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


def main():
    with open("./scripts/05_plot_params_hedgehog.json", "r") as f:
        plot_params = json.load(f)
    for key in plot_params["rcparams"]:
        mpl.rcParams[key] = plot_params["rcparams"][key]
    folderplot = FOLDEROOTS + "plots/hedgehog"
    if not os.path.exists(folderplot):
        os.makedirs(folderplot)
    for met_growth, cmap in {
        "coverage": mpl.colormaps["Blues"],
        "directness": mpl.colormaps["Oranges"],
        "betweenness": mpl.colormaps["Greens"],
    }.items():
        for met_plot, met_label in {
            "coverage": "Coverage ($km^2$)",
            "directness": "Directness",
            "directness_alt": "Directness (alt)",
            "num_cc": "Number of components",
            "length_lcc": "Length of LCC (km)",
        }.items():
            fig, ax = plt.subplots(figsize=plot_params["figsize"])
            if met_plot == "coverage":
                ratio = 10**6
            elif met_plot == "length_lcc":
                ratio = 10**3
            else:
                ratio = 1
            ax.set_ylabel(met_label)
            colors = cmap(np.linspace(0, 1, len(TIMESTAMPS) + 7))
            for idx, t in enumerate(TIMESTAMPS):
                foldertime = FOLDEROOTS + t + "/"
                foldermet_real = foldertime + "real/"
                df = pd.read_json(foldermet_real + "metrics_growth.json")
                if t == "No":
                    ax.scatter(
                        [df["xx"].values[0] / 10**3],
                        [df[met_plot].values[0] / ratio],
                        color="black",
                        marker=".",
                        s=300,
                    )
                ax.plot(
                    df["xx"] / 10**3,
                    df[met_plot] / ratio,
                    color="black",
                    marker="*",
                    markersize=10,
                )
                foldermet_met = foldertime + met_growth + "_additive_connected"
                if t != "No":
                    foldermet_met += "_built"
                foldermet_met += "/"
                df = pd.read_json(foldermet_met + "metrics_growth.json")
                ax.plot(
                    df["xx"] / 10**3,
                    df[met_plot] / ratio,
                    color=colors[idx + 5],
                )
            ax.set_xlabel("Built length ($km$)")
            ax.set_axisbelow(True)
            plt.tight_layout()
            # plt.legend()
            plt.savefig(
                folderplot
                + f"/{met_growth}_growth_{met_plot}_plot_additive_hedgehog.png"
            )
            plt.close()


def average_x(df):
    arr = []
    for ind in set(df.index):
        arr.append(df[df.index == ind].mean())
    return arr


if __name__ == "__main__":
    main()
