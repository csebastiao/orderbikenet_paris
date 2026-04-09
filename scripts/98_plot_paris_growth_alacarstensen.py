# -*- coding: utf-8 -*-
"""
Plot paris bicycle network growth at four timestamps.
"""


import osmnx as ox
import matplotlib.pyplot as plt


GPKG_PATH = "./data/raw/paris_en_selle_map_updates/cleaned.gpkg"
SAVEPATH = "./data/processed/paris_simplified_results/"


def main():
    G = ox.load_graphml(
        "./data/processed/paris_simplified_results/paris_cleaned_multigraph.graphml"
    )
    edges = ox.graph_to_gdfs(G, edges=True, nodes=False)
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
    fig, axs = plt.subplots(2, 2, figsize=(12, 9), layout="constrained")
    axs[0][0].axis("off")
    axs[0][0].set_title(TIMESTAMPS[0], fontname="Arial", fontsize=20, fontweight="bold")
    axs[0][1].set_title(TIMESTAMPS[1], fontname="Arial", fontsize=20, fontweight="bold")
    axs[1][0].set_title(
        TIMESTAMPS[-2], fontname="Arial", fontsize=20, fontweight="bold"
    )
    axs[1][1].set_title(
        TIMESTAMPS[-1], fontname="Arial", fontsize=20, fontweight="bold"
    )
    axs[0][1].axis("off")
    axs[1][0].axis("off")
    axs[1][1].axis("off")
    edges[edges["built"] == "2021-01-01"].plot(ax=axs[0][0], color="black")
    edges[edges["built"].isin(TIMESTAMPS[:2])].plot(ax=axs[0][1], color="black")
    edges[edges["built"].isin(TIMESTAMPS[:-1])].plot(ax=axs[1][0], color="black")
    edges.plot(ax=axs[1][1], color="black")
    fig.savefig(
        "./data/processed/paris_simplified_results/plots/bikenetgrowth.png", dpi=300
    )


if __name__ == "__main__":
    main()
