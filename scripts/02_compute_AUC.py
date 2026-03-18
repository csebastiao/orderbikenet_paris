# -*- coding: utf-8 -*-
"""
Script to compute the Area Under the Curve of all metrics for all strategies for all timestamps.
"""

import json
import pandas as pd
import networkx as nx
import osmnx as ox
from orderbike.utils import auc_from_metrics_dict, get_auc
from orderbike.metrics import directness, coverage

FOLDEROOTS = "./data/processed/paris_simplified_results/"
RAND_TRIAL_NUMBER = 50
BUFF_SIZE = 400


if __name__ == "__main__":
    # With and without exponential discounting
    G = ox.load_graphml(FOLDEROOTS + "paris_cleaned_multigraph.graphml")
    closeness = nx.closeness_centrality(G, distance="length")
    edge_closeness = {}
    for edge in G.edges:
        edge_closeness[edge] = (closeness[edge[0]] + closeness[edge[1]]) / 2
    init_edge = [tuple(max(edge_closeness, key=edge_closeness.get))]
    G_init = G.edge_subgraph(init_edge)
    tot_length = [sum([G_init.edges[e]["length"] for e in G_init.edges])]
    dir_real = [directness(G_init)]
    cov_real = [coverage(G_init, BUFF_SIZE)]
    timestamps = [
        "2021 and before",
        "2023-05-17",
        "2023-10-01",
        "2024-01-15",
        "2024-04-04",
        "2024-08-22",
        "2024-12-22",
        "2025-06-02",
        "No",
    ]
    for idx, t in enumerate(timestamps):
         H = G.edge_subgraph([e for e in G.edges if G.edges[e]["built"] in timestamps[:idx+1]])
         tot_length.append(sum([H.edges[e]["length"] for e in H.edges]))
         dir_real.append(directness(H))
         cov_real.append(coverage(H, BUFF_SIZE))
    for exp_disc in [True, False]:
        timestamp_aucs = [] 
        for idx, t in enumerate(timestamps):
            foldertime = FOLDEROOTS + t + "/"
            # Open for all growth strategies for a toy graph
            for metric in [
                "adaptive_coverage",
                "coverage",
                "relative_directness",
                "directness",
                "betweenness",
                "closeness",
                "random",
                "real",
            ]:
                foldermetric = foldertime + metric + "_additive_connected"
                if t == "No":
                    foldermetric += "/"
                else:
                    foldermetric += "_built/"
                if metric == "random":
                    for i in range(RAND_TRIAL_NUMBER):
                        with open(foldermetric + f"metrics_growth_{i:02}.json", "r") as f:
                            met_dict = json.load(f)
                        auc_cov = auc_from_metrics_dict(
                            met_dict,
                            "coverage",
                            normalize_y=True,
                            yaxis_method="natural",
                            exp_discounting=exp_disc,
                        )
                        auc_dir = auc_from_metrics_dict(
                            met_dict,
                            "directness",
                            normalize_y=False,
                            max_comparison_y="one",
                            exp_discounting=exp_disc,
                        )
                        timestamp_aucs.append(
                            [t, metric, i, auc_cov, auc_dir]
                        )
                elif metric == "real":
                    auc_dir = get_auc(
                        tot_length[idx:],
                        dir_real[idx:],
                        normalize_y=False,
                        max_comparison_y="one",
                        exp_discounting=False,
                    )
                    auc_cov = get_auc(
                        tot_length[idx:],
                        cov_real[idx:],
                        normalize_y=True,
                        yaxis_method="natural",
                        exp_discounting=False,
                    )
                    timestamp_aucs.append(
                        [t, metric, 0, auc_cov, auc_dir]
                    )
                else:
                    with open(foldermetric + "metrics_growth.json", "r") as f:
                            met_dict = json.load(f)
                    auc_cov = auc_from_metrics_dict(
                        met_dict,
                        "coverage",
                        normalize_y=True,
                        yaxis_method="natural",
                        exp_discounting=exp_disc,
                    )
                    auc_dir = auc_from_metrics_dict(
                        met_dict,
                        "directness",
                        normalize_y=False,
                        max_comparison_y="one",
                        exp_discounting=exp_disc,
                    )
                    timestamp_aucs.append(
                        [t, metric, 0, auc_cov, auc_dir]
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
            ],
        )
        savename = str(FOLDEROOTS) + "auc_table_growth_additive"
        if exp_disc:
            savename += "_expdisc"
        savename += ".json"
        df_growth.to_json(savename)
