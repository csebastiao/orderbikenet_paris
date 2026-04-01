# -*- coding: utf-8 -*-
"""
Find growth order on Paris graph, with all growth strategies, dynamic and ranked, and random trials.
"""


import os
import json
import osmnx as ox
from orderbike import growth, metrics
from orderbike.utils import log


GRAPH_NAME = "Paris"
FOLDEROOTS = "./data/processed/paris_simplified_results"
FILENAME = "paris_cleaned_multigraph.graphml"
BUFF_SIZE = 400
NUM_RAND_TRIAL = 50
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
PAD = len(str(NUM_RAND_TRIAL - 1))


# FIXME test of valid edges in subtractive order to make it faster (take ages right now !)
# FIXME error edges are not well named
def main():
    ranking_func = {}
    ranking_func["closeness"] = metrics.growth_closeness
    ranking_func["betweenness"] = metrics.growth_betweenness
    G = ox.load_graphml(FOLDEROOTS + "/" + FILENAME)
    log.info(f"Start graph {GRAPH_NAME}")
    for idx, built_val in enumerate(TIMESTAMPS):
        foldertime = FOLDEROOTS + "/" + built_val
        if not os.path.exists(foldertime):
            os.makedirs(foldertime)
        log.info(f"Start computation for timestamp {built_val}")
        H = G.copy()
        if built_val == "No":
            built = False
        else:
            built = True
            for e in H.edges:
                if H.edges[e]["built"] in TIMESTAMPS[: idx + 1]:
                    H.edges[e]["built"] = 1
                else:
                    H.edges[e]["built"] = 0
        for order_name in [
            "additive",
            "subtractive",
        ]:
            if built_val != "2021-01-01" and order_name == "subtractive":
                pass
            else:
                for metric_name in [
                    # "adaptive_coverage",
                    # "coverage",
                    # "directness",
                    # "relative_directness",
                    "directness_alt"
                ]:
                    log.info(
                        f"Start computation for metric {metric_name}, order {order_name}"
                    )
                    if metric_name == "coverage":
                        kwargs = {"buff_size": BUFF_SIZE}
                    elif metric_name == "adaptive_coverage":
                        kwargs = {"max_buff": BUFF_SIZE * 2, "min_buff": BUFF_SIZE / 2}
                    else:
                        kwargs = {}
                    foldername = (
                        foldertime + "/" + metric_name + "_" + order_name + "_connected"
                    )
                    if built:
                        foldername += "_built"
                    if not os.path.exists(foldername):
                        os.makedirs(foldername)
                    metrics_dict, order_growth = growth.order_dynamic_network_growth(
                        H,
                        built=built,
                        keep_connected=True,
                        order=order_name,
                        metric=metric_name,
                        progress_bar=False,
                        save_metrics=True,
                        buff_size_metrics=BUFF_SIZE,
                        **kwargs,
                    )
                    with open(foldername + "/order_growth.json", "w") as f:
                        json.dump(order_growth, f)
                    with open(foldername + "/metrics_growth.json", "w") as f:
                        json.dump(metrics_dict, f)
                # for metric_name in ranking_func:
                #     log.info(
                #         f"Start computation for metric {metric_name}, order {order_name}"
                #     )
                #     foldername = (
                #         foldertime + "/" + metric_name + "_" + order_name + "_connected"
                #     )
                #     if built:
                #         foldername += "_built"
                #     if not os.path.exists(foldername):
                #         os.makedirs(foldername)
                #     metrics_dict, order_growth = growth.order_ranked_network_growth(
                #         H,
                #         built=built,
                #         keep_connected=True,
                #         order=order_name,
                #         ranking_func=ranking_func[metric_name],
                #         save_metrics=True,
                #         buff_size_metrics=BUFF_SIZE,
                #     )
                #     with open(foldername + "/order_growth.json", "w") as f:
                #         json.dump(order_growth, f)
                #     with open(foldername + "/metrics_growth.json", "w") as f:
                #         json.dump(metrics_dict, f)
                # log.info(f"Start random computation, order {order_name}")
                # foldername = foldertime + "/" + "random_" + order_name + "_connected"
                # if built:
                #     foldername += "_built"
                # if not os.path.exists(foldername):
                #     os.makedirs(foldername)
                # for i in range(NUM_RAND_TRIAL):
                #     log.info(f"Start trial {i}")
                #     metrics_dict, order_growth = growth.order_ranked_network_growth(
                #         H,
                #         built=built,
                #         keep_connected=True,
                #         order=order_name,
                #         ranking_func=metrics.growth_random,
                #         save_metrics=True,
                #         buff_size_metrics=BUFF_SIZE,
                #     )
                #     with open(foldername + f"/order_growth_{i:0{PAD}}.json", "w") as f:
                #         json.dump(order_growth, f)
                #     with open(foldername + f"/metrics_growth_{i:0{PAD}}.json", "w") as f:
                #         json.dump(metrics_dict, f)
    log.info("Finished !")


if __name__ == "__main__":
    main()
