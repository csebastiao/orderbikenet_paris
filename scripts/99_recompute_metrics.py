# -*- coding: utf-8 -*-
"""
Recompute metric for every growth order.
"""


import tqdm
import json
import osmnx as ox
from orderbike.growth import compute_metrics


FOLDEROOTS = "./data/processed/paris_simplified_results/"
RAND_TRIAL_NUMBER = 50
TIMESTAMPS = [
    # "2021-01-01",
    # "2023-05-17",
    "2023-10-01",
    # "2024-01-15",
    # "2024-04-04",
    # "2024-08-22",
    # "2024-12-22",
    "2025-06-02",
    # "No",
]
METRIC_LIST = [
    "adaptive_coverage",
    "coverage",
    "relative_directness",
    "directness",
    "betweenness",
    "closeness",
    "random",
]


def main():
    G = ox.load_graphml(FOLDEROOTS + "paris_cleaned_multigraph.graphml")
    for idx, t in enumerate(tqdm.tqdm(TIMESTAMPS)):
        foldertime = FOLDEROOTS + t + "/"
        H = G.copy()
        if t == "No":
            built = False
        else:
            built = True
            for e in G.edges:
                if G.edges[e]["built"] in TIMESTAMPS[: idx + 1]:
                    H.edges[e]["built"] = 1
                else:
                    H.edges[e]["built"] = 0
        for metric in METRIC_LIST:
            foldermet = foldertime + metric + "_subtractive_connected"
            if t != "No":
                foldermet += "_built"
            foldermet += "/"
            if metric == "random":
                for i in range(RAND_TRIAL_NUMBER):
                    with open(foldermet + f"order_growth_{i:02}.json", "r") as f:
                        order_growth = json.load(f)
                    order_growth = [tuple(val) for val in order_growth]
                    met_dict = compute_metrics(H, order_growth, built=built)
                    # edges_grown = init_edges.copy()
                    # arr_dir_alt = [directness_alt(G.edge_subgraph(edges_grown))]
                    # for e in order_growth:
                    #     edges_grown.append(e)
                    #     arr_dir_alt.append(directness_alt(G.edge_subgraph(edges_grown)))
                    # with open(foldermet + f"metrics_growth_{i:02}.json", "r") as f:
                    #     met_dict = json.load(f)
                    # met_dict["directness_alt"] = arr_dir_alt
                    with open(foldermet + f"metrics_growth_{i:02}.json", "w") as f:
                        json.dump(met_dict, f)
            else:
                with open(foldermet + "order_growth.json", "r") as f:
                    order_growth = json.load(f)
                order_growth = [tuple(val) for val in order_growth]
                met_dict = compute_metrics(H, order_growth, built=built)
                # edges_grown = init_edges.copy()
                # arr_dir_alt = [directness_alt(G.edge_subgraph(edges_grown))]
                # for e in order_growth:
                #     edges_grown.append(e)
                #     arr_dir_alt.append(directness_alt(G.edge_subgraph(edges_grown)))
                # with open(foldermet + "metrics_growth.json", "r") as f:
                #     met_dict = json.load(f)
                # met_dict["directness_alt"] = arr_dir_alt
                with open(foldermet + "metrics_growth.json", "w") as f:
                    json.dump(met_dict, f)


if __name__ == "__main__":
    main()
