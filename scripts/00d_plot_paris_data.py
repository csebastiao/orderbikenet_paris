# -*- coding: utf-8 -*-
"""
Create paris demographics processed files from raw files.
"""


import os
import geopandas as gpd
import matplotlib.pyplot as plt


FOLDER_DATA = "./data/processed/paris_official_data/"
PARTY_DICT = {
    "LUC": "Purples",
    "LUD": "Blues",
    "LUG": "Reds",
}
DPI = 300


def main():
    folderplots = FOLDER_DATA + "plots/"
    if not os.path.exists(folderplots):
        os.makedirs(folderplots)
    gdf_pop = gpd.read_file(FOLDER_DATA + "paris_dem_iris_condensed_enriched.gpkg")
    for column_name, cmap in {
        "population": "inferno",
        "pop_density": "inferno",
        "poverty_rate": "Reds",
        "median_income": "Greens",
        "commuter_cyclist_share": "Greens",
        "commuter_driver_share": "Reds",
        "Restauration": "inferno",
        "Restauration_density": "inferno",
    }.items():
        fig, ax = plt.subplots(layout="constrained")
        gdf_pop.plot(
            ax=ax, column=column_name, cmap=cmap, legend=True, scheme="fisher_jenks"
        )
        ax.axis("off")
        fig.savefig(folderplots + "Paris_" + column_name + "_IRIS.png", dpi=DPI)
    gdf_vote = gpd.read_file(FOLDER_DATA + "paris_vote_list.gpkg")
    for party, color in PARTY_DICT.items():
        fig, ax = plt.subplots(layout="constrained")
        gdf_vote.plot(
            ax=ax,
            column=party + "_share",
            cmap=color,
            vmin=0,
            vmax=1,
            edgecolor="black",
            linewidth=0.1,
            legend=True,
        )
        ax.axis("off")
        fig.savefig(folderplots + "Paris_vote_" + party + ".png", dpi=DPI)
    gdf_metro = gpd.read_file(FOLDER_DATA + "idf_metro.gpkg")
    fig, ax = plt.subplots(layout="constrained")
    gpd.GeoDataFrame(geometry=[gdf_vote.union_all()], crs=gdf_vote.crs).boundary.plot(
        ax=ax, edgecolor="black", linewidth=1
    )
    gdf_metro.plot(ax=ax, color="red", markersize=5, linewidth=0.1)
    ax.axis("off")
    fig.savefig(folderplots + "Paris_simplified_metro.png", dpi=DPI)


if __name__ == "__main__":
    main()
