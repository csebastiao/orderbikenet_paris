"""
Plot every additive growth strategies.
"""

import json
import os
import osmnx as ox
from orderbike.plot import plot_growth

FOLDEROOTS = "./data/processed/paris_simplified_results/"
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
BUFF_SIZE = 400
BUFFER = True
PLOT_METRICS = False
DPI = 100  # Larger means bigger files and longer to save, and there are a lot of pictures so quickly taking space and time
MET_LIST = [
    "adaptive_coverage",
    "coverage",
    "relative_directness",
    "directness",
    "betweenness",
    "closeness",
]


def main():
    G = ox.load_graphml(FOLDEROOTS + "/" + FILENAME)
    folderplot = FOLDEROOTS + "plots/growths/"
    if not os.path.exists(folderplot):
        os.makedirs(folderplot)
    for idx, t in enumerate(TIMESTAMPS):
        H = G.copy()
        if t == "No":
            built = False
        else:
            built = True
            for e in H.edges:
                if H.edges[e]["built"] in TIMESTAMPS[: idx + 1]:
                    H.edges[e]["built"] = 1
                else:
                    H.edges[e]["built"] = 0
        foldertime = FOLDEROOTS + t + "/"
        foldertimeplot = folderplot + t + "/"
        if not os.path.exists(foldertimeplot):
            os.makedirs(foldertimeplot)
        for met in MET_LIST:
            foldermet = foldertime + met + "_additive_connected"
            if t != "No":
                foldermet += "_built"
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
    # Plot real growth
    folderrealplot = folderplot + "real/"
    if not os.path.exists(folderrealplot):
        os.makedirs(folderrealplot)
    with open(FOLDEROOTS + "No/real/order_growth.json") as f:
        order_growth = json.load(f)
    order_growth = [tuple(val) for val in order_growth]
    with open(FOLDEROOTS + "No/real/metrics_growth.json") as f:
        metrics_dict = json.load(f)
    plot_growth(
        G,
        order_growth,
        folderrealplot,
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


if __name__ == "__main__":
    main()
