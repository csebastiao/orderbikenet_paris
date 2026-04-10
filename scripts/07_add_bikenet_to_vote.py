# -*- coding: utf-8 -*-
"""
Add progress of bicycle plans to arrondissements.
"""

import numpy as np
import pandas as pd
import shapely
import geopandas as gpd
import osmnx as ox
from scipy.spatial import KDTree


FOLDER_BIKE = "./data/processed/paris_simplified_results/"
FOLDER_OFFI = "./data/processed/paris_official_data/"


def main():
    G = ox.load_graphml(FOLDER_BIKE + "paris_cleaned_multigraph.graphml")
    gdf_edges = ox.graph_to_gdfs(G, edges=True, nodes=False)
    gdf_edges = gdf_edges[["geometry", "length", "built"]]
    gdf_vote_arr = gpd.read_file(FOLDER_OFFI + "paris_vote_arr.gpkg")
    gdf_vote_arr = gdf_vote_arr.to_crs(gdf_edges.crs)
    gdf_vote_arr_res = add_length_to_poly(gdf_vote_arr, gdf_edges)
    gdf_vote_arr_res.to_file(FOLDER_BIKE + "paris_vote_arr_bikenet.gpkg")
    gdf_vote_sta = gpd.read_file(FOLDER_OFFI + "paris_vote_list.gpkg")
    gdf_vote_sta = gdf_vote_sta.to_crs(gdf_edges.crs)
    gdf_vote_sta_res = add_length_to_poly(gdf_vote_sta, gdf_edges)
    centroids = np.array(
        [[point.x, point.y] for point in gdf_vote_sta_res.geometry.centroid]
    )
    kdtree = KDTree(centroids)
    gdf_vote_sta_res["length_accomplished_share_smoothed"] = spatial_smoothing_gaussian(
        gdf_vote_sta_res["length_accomplished_share"].values,
        centroids,
        kdtree,
        k=20,
        bandwidth=200,
    )
    gdf_vote_sta_res.to_file(FOLDER_BIKE + "paris_vote_sta_bikenet.gpkg")


def add_length_to_poly(gdf_poly, gdf_edges):
    gdf_poly_edges = gdf_poly.sjoin(gdf_edges, how="left", predicate="intersects")
    results_dict = {}
    for idx, row in gdf_poly_edges.iterrows():
        if isinstance(row["built"], str):
            length = shapely.intersection(
                row["geometry"],
                gdf_edges.loc[row["u"], row["v"], row["key"]]["geometry"],
            ).length
        else:
            length = 0
        planned = 0
        before = 0
        built = 0
        if row["built"] == "No":
            planned += length
        elif row["built"] == "2021-01-01":
            before += length
        else:
            planned += length
            built += length
        if idx not in results_dict.keys():
            results_dict[idx] = {
                "length_before_2021": before,
                "length_planned": planned,
                "length_built": built,
            }
        else:
            results_dict[idx]["length_before_2021"] += before
            results_dict[idx]["length_planned"] += planned
            results_dict[idx]["length_built"] += built
    df = pd.DataFrame.from_dict(results_dict, orient="index")
    gdf_poly_res = gdf_poly.merge(df, left_index=True, right_index=True)
    gdf_poly_res["length_accomplished_share"] = (
        gdf_poly_res["length_built"] / gdf_poly_res["length_planned"]
    )
    gdf_poly_res["length_final"] = (
        gdf_poly_res["length_before_2021"] + gdf_poly_res["length_planned"]
    )
    for col in [
        "length_before_2021",
        "length_planned",
        "length_built",
        "length_final",
    ]:
        gdf_poly_res[col + "_norm"] = (gdf_poly_res[col] / 10**3) / (
            gdf_poly_res["geometry"].area / 10**6
        )
    return gdf_poly_res


# from https://medium.com/@1998ameya/introduction-to-spatial-smoothing-with-python-4eaa8db6279c
def spatial_smoothing_gaussian(values, centroids, kdtree, k=10, bandwidth=0.1):
    smoothed_values = np.zeros_like(values)
    for i, centroid in enumerate(centroids):
        distances, indices = kdtree.query(centroid, k=k)
        weights = np.exp(-(distances**2) / (2 * bandwidth**2))
        smoothed_values[i] = np.sum(
            [val * w for val, w in zip(values[indices], weights) if not np.isnan(val)]
        ) / np.sum([w for val, w in zip(values[indices], weights) if not np.isnan(val)])
    return smoothed_values


if __name__ == "__main__":
    main()
