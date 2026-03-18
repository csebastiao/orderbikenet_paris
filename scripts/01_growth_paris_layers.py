# -*- coding: utf-8 -*-
"""
Script to find growth order on Paris graph, with all growth strategies, dynamic and ranked, and random trials.
"""

import os
import json
from orderbike import growth, metrics
from orderbike.utils import log
import osmnx as ox
import os


#TODO: Fix test of valid edges in subtractive order to make it faster (take ages right now !)
#TODO: Fix error edges are not well named
if __name__ == "__main__":
    CONNECTED = True
    ranking_func = {}
    ranking_func["closeness"] = metrics.growth_closeness
    ranking_func["betweenness"] = metrics.growth_betweenness
    BUFF_SIZE = 400
    NUM_RAND_TRIAL = 50
    graph_name = "Paris"
    folderoots = "./data/processed/paris_simplified_results"
    G = ox.load_graphml(folderoots + "/paris_cleaned_multigraph.graphml")
    PAD = len(str(NUM_RAND_TRIAL - 1))
    log.info(f"Start graph {graph_name}")
    timestamps = [
        # "2021 and before",
        # "2023-05-17",
        # "2023-10-01",
        # "2024-01-15",
        # "2024-04-04",
        # "2024-08-22",
        # "2024-12-22",
        # "2025-06-02",
        "No",
    ]
    for idx, built_val in enumerate(timestamps):
        foldertime = folderoots + "/" + built_val
        if not os.path.exists(foldertime):
            os.makedirs(foldertime)
        log.info(
                    f"Start computation for timestamp {built_val}"
                )
        H = G.copy()
        if built_val == "No":
            BUILT = False
        else:
            BUILT = True
            for e in H.edges:
                if H.edges[e]["built"] in timestamps[:idx+1]:
                    H.edges[e]["built"] = 1
                else:
                    H.edges[e]["built"] = 0
        for ORDERNAME in [
            "additive",
            "subtractive",
        ]:
            for METRICNAME in [
                "adaptive_coverage",
                "coverage",
                "directness",
                "relative_directness",
            ]:
                log.info(
                    f"Start computation for metric {METRICNAME}, order {ORDERNAME}"
                )
                if METRICNAME == "coverage":
                    kwargs = {"buff_size": BUFF_SIZE}
                elif METRICNAME == "adaptive_coverage":
                    kwargs = {"max_buff": BUFF_SIZE * 2, "min_buff": BUFF_SIZE / 2}
                else:
                    kwargs = {}
                foldername = foldertime + "/" + METRICNAME + "_" + ORDERNAME
                if CONNECTED:
                    foldername += "_connected"
                if BUILT:
                    foldername += "_built"
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                metrics_dict, order_growth = growth.order_dynamic_network_growth(
                    H,
                    built=BUILT,
                    keep_connected=CONNECTED,
                    order=ORDERNAME,
                    metric=METRICNAME,
                    progress_bar=False,
                    save_metrics=True,
                    buff_size_metrics=BUFF_SIZE,
                    **kwargs,
                )
                with open(foldername + "/order_growth.json", "w") as f:
                    json.dump(order_growth, f)
                with open(foldername + "/metrics_growth.json", "w") as f:
                    json.dump(metrics_dict, f)
            for METRICNAME in ranking_func:
                log.info(
                    f"Start computation for metric {METRICNAME}, order {ORDERNAME}"
                )
                foldername = foldertime + "/" + METRICNAME + "_" + ORDERNAME
                if CONNECTED:
                    foldername += "_connected"
                if BUILT:
                    foldername += "_built"
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                metrics_dict, order_growth = growth.order_ranked_network_growth(
                    H,
                    built=BUILT,
                    keep_connected=CONNECTED,
                    order=ORDERNAME,
                    ranking_func=ranking_func[METRICNAME],
                    save_metrics=True,
                    buff_size_metrics=BUFF_SIZE,
                )
                with open(foldername + "/order_growth.json", "w") as f:
                    json.dump(order_growth, f)
                with open(foldername + "/metrics_growth.json", "w") as f:
                    json.dump(metrics_dict, f)
            log.info(f"Start random computation, order {ORDERNAME}")
            foldername = foldertime + "/" + "random_" + ORDERNAME
            if CONNECTED:
                foldername += "_connected"
            if BUILT:
                foldername += "_built"
            if not os.path.exists(foldername):
                os.makedirs(foldername)
            for i in range(NUM_RAND_TRIAL):
                log.info(f"Start trial {i}")
                metrics_dict, order_growth = growth.order_ranked_network_growth(
                    H,
                    built=BUILT,
                    keep_connected=CONNECTED,
                    order=ORDERNAME,
                    ranking_func=metrics.growth_random,
                    save_metrics=True,
                    buff_size_metrics=BUFF_SIZE,
                )
                with open(foldername + f"/order_growth_{i:0{PAD}}.json", "w") as f:
                    json.dump(order_growth, f)
                with open(foldername + f"/metrics_growth_{i:0{PAD}}.json", "w") as f:
                    json.dump(metrics_dict, f)
        log.info("Finished !")
