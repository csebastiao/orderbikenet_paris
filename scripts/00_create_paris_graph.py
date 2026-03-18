# -*- coding: utf-8 -*-
"""
From a list of LineStrings, create a simplified networkx street network of Paris. The list of LineStrings is a manually modified version of the Paris en Selle data.
"""


import geopandas as gpd
import momepy as mp
import networkx as nx
import osmnx as ox


GPKG_PATH = "./data/raw/paris_en_selle_map_updates/cleaned.gpkg"
SAVEPATH = "./data/processed/paris_simplified_results/"


def main():
    # Read the GeoPackage manually made from QGIS
    gdf = gpd.read_file(GPKG_PATH)
    if "fid" in gdf.columns:
        gdf = gdf.drop(columns=["fid"])
    gdf_ls = gdf.copy()
    gdf_ls["length"] = gdf_ls.geometry.length
    # Get a networkx MultiDigraph and add node coordinates
    G = mp.gdf_to_nx(gdf_ls, multigraph=True, directed=True, length="length")
    for n in G:
        G.nodes[n]["x"] = n[0]
        G.nodes[n]["y"] = n[1]
    H = G.copy()
    # Segmentize by having all edges being straight edges so osmnx can simplify it
    for e in G.edges:
        if len(G.edges[e]["geometry"].coords[:]) > 2:
            raise ValueError(f"See edge {e} with more than 2 coords !")
    H = nx.convert_node_labels_to_integers(H)
    for e in H.edges:
        if H.edges[e]["2023-05-17 Etat"] in "Réalisé Pré-2021":
            H.edges[e]["built"] = "2021-01-01"
        elif H.edges[e]["2023-05-17 Etat"] in ["Réalisé dans le Plan Vélo", "Annoncé réalisé", "Hors Plan Vélo (Embellir)"]:
            H.edges[e]["built"] = "2023-05-17"
        elif H.edges[e]["2023-10-01 Etat"] in ["Réalisé dans le Plan Vélo", "Annoncé réalisé", "Hors Plan Vélo (Embellir)"]:
            H.edges[e]["built"] = "2023-10-01"
        elif H.edges[e]["2024-01-15 Etat"] in ["Réalisé dans le Plan Vélo", "Annoncé réalisé", "Hors Plan Vélo (Embellir)"]:
            H.edges[e]["built"] = "2024-01-15"
        elif H.edges[e]["2024-04-04 Etat"] in ["Réalisé dans le Plan Vélo", "Annoncé réalisé", "Hors Plan Vélo (Embellir)"]:
            H.edges[e]["built"] = "2024-04-04"
        elif H.edges[e]["2024-08-22 Etat"] in ["Réalisé dans le Plan Vélo", "Annoncé réalisé", "Hors Plan Vélo (Embellir)"]:
            H.edges[e]["built"] = "2024-08-22"
        elif H.edges[e]["2024-12-22 Etat"] in ["Réalisé dans le Plan Vélo", "Annoncé réalisé", "Hors Plan Vélo (Embellir)"]:
            H.edges[e]["built"] = "2024-12-22"
        elif H.edges[e]["Etat"] in ["Réalisé dans le Plan Vélo", "Annoncé réalisé", "Hors Plan Vélo (Embellir)"]:
            H.edges[e]["built"] = "2025-06-02"
        else:
            H.edges[e]["built"] = "No"
    # Simplify while keeping the attribute about built and planned discriminated
    H = ox.simplify_graph(H, edge_attrs_differ=["built"])
    ox.save_graphml(
        H,
        filepath=SAVEPATH + "paris_cleaned_multidigraph.graphml",
    )
    nx.set_edge_attributes(H, 0, "osmid")
    H = ox.convert.to_undirected(H)
    ox.save_graphml(
        H,
        filepath=SAVEPATH + "paris_cleaned_multigraph.graphml",
    )
    ox.save_graph_geopackage(
        H,
        filepath=SAVEPATH + "paris_cleaned_multigraph.gpkg",
    )


if __name__ == "__main__":
   main()