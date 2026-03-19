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
    for exp_disc in [True, False]:
        timestamp_aucs = [] 
        for idx, t in enumerate(TIMESTAMPS):
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
                foldermet = foldertime + metric
                if metric!= "real":
                    foldermet+= "_additive_connected"
                    if t != "No":
                        foldermet += "_built"
                foldermet += "/"
                if metric == "random":
                    for i in range(RAND_TRIAL_NUMBER):
                        with open(foldermet + f"metrics_growth_{i:02}.json", "r") as f:
                            met_dict = json.load(f)
                        auc_cov = auc_from_metrics_dict(
                            met_dict,
                            "coverage",
                            normalize_y=True,
                            yaxis_method="natural",
                            exp_discounting=exp_disc,
                            normalize_max_auc=False,
                        )
                        auc_dir = auc_from_metrics_dict(
                            met_dict,
                            "directness",
                            normalize_y=False,
                            max_comparison_y="one",
                            exp_discounting=exp_disc,
                            normalize_max_auc=False,
                        )
                        timestamp_aucs.append(
                            [t, metric, i, auc_cov, auc_dir]
                        )
                else:
                    with open(foldermet + "metrics_growth.json", "r") as f:
                            met_dict = json.load(f)
                    auc_cov = auc_from_metrics_dict(
                        met_dict,
                        "coverage",
                        normalize_y=True,
                        yaxis_method="natural",
                        exp_discounting=exp_disc,
                        normalize_max_auc=False,
                    )
                    auc_dir = auc_from_metrics_dict(
                        met_dict,
                        "directness",
                        normalize_y=False,
                        max_comparison_y="one",
                        exp_discounting=exp_disc,
                        normalize_max_auc=False,
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


if __name__ == "__main__":
    main()