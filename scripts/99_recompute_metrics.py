# -*- coding: utf-8 -*-
"""
Recompute all metrics for every growth order.
"""


import pathlib
import json
import osmnx as ox
from orderbike.growth import compute_metrics


FOLDEROOTS = "./data/processed/paris_simplified_results/"
TARGET = "order_growth***.json"
BUFFER_SIZE = 400


def main():
    G = ox.load_graphml(FOLDEROOTS + "paris_cleaned_multigraph.graphml")
    source_dir = pathlib.Path(FOLDEROOTS)
    for f in source_dir.rglob(TARGET):
        splitted = str(f).split("/")
        folder = "/".join(splitted[:-1])
        with open(f, "r") as f:
            order_growth = json.load(f)
        order_growth = [tuple(val) for val in order_growth]
        met_dict = compute_metrics(G, order_growth, buff_size=BUFFER_SIZE)
        met_dict_filename = (
            "/metrics_growth"
            + splitted[-1].removeprefix("order_growth").removesuffix(".json")
            + ".json"
        )
        with open(folder + met_dict_filename, "w") as f:
            json.dump(met_dict, f)


if __name__ == "__main__":
    main()
