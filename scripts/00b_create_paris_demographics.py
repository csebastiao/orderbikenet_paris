# -*- coding: utf-8 -*-
"""
Create paris demographics processed files from raw files.
"""

import os
import geopandas as gpd
import pandas as pd

FOLDER_IN = "./data/raw/official_data/"
FOLDER_OUT = "./data/processed/paris_official_data/"


def main():
    if not os.path.exists(FOLDER_OUT):
        os.makedirs(FOLDER_OUT)
    li = []
    for i in range(1, 21):
        if i == 7:
            li.append(
                pd.read_excel(
                    FOLDER_IN
                    + f"votingparis_values_2020/DDCT_BERP_municipales_2020_tour1_Ardt_{i:02}_20200315.xls"
                )
            )
        else:
            li.append(
                pd.read_excel(
                    FOLDER_IN
                    + f"votingparis_values_2020/DDCT_BERP_municipales_2020_tour2_Ardt_{i:02}_20200628.xls"
                )
            )
    df_paris_vote = pd.concat(li, axis=0)
    df_paris_vote = df_paris_vote.rename({"ID_BVOTE": "id_bv"}, axis=1)
    names = list(
        df_paris_vote.drop(
            [
                "id_bv",
                "SCRUTIN",
                "ANNEE",
                "TOUR",
                "DATE",
                "NUM_CIRC",
                "NUM_QUARTIER",
                "NUM_ARROND",
                "NUM_BUREAU",
                "NB_PROCU",
                "NB_INSCR",
                "NB_EMARG",
                "NB_VOTANT",
                "NB_BLANC",
                "NB_NUL",
                "NB_EXPRIM",
            ],
            axis=1,
        )
    )
    nuances = [
        "LUC",
        "LUD",
        "LUG",
        "LUG",
        "LUD",
        "LUG",
        "LUC",
        "LUD",
        "LUD",
        "LDVD",
        "LRN",
        "LUC",
        "LUG",
        "LFI",
        "LVEC",
        "LDIV",
        "LDIV",
        "LDVC",
        "LUD",
        "LDVD",
        "LUG",
        "LUC",
        "LUD",
        "LUC",
        "LUG",
        "LUD",
        "LUG",
        "LUC",
        "LUD",
        "LUG",
        "LUC",
        "LUG",
        "LUC",
        "LUD",
        "LUC",
        "LUG",
        "LUD",
        "LDVC",
        "LUD",
        "LUC",
        "LUG",
        "LUC",
        "LUD",
        "LUG",
        "LUD",
        "LUC",
        "LUC",
        "LUD",
        "LUG",
        "LUG",
        "LUC",
        "LUD",
        "LDVC",
        "LUG",
        "LUD",
        "LUG",
        "LUD",
        "LFI",
        "LUC",
    ]
    candidates = {name: nuance for name, nuance in zip(names, nuances)}
    alignment_nuances = {
        "LEXG": 0,
        "LCOM": 1,
        "LFI": 2,
        "LSOC": 3,
        "LRDG": 4,
        "LDVG": 5,
        "LUG": 6,
        "LVEC": 7,
        "LECO": 8,
        "LDIV": 9,
        "LREG": 10,
        "LGJ": 11,
        "LREM": 12,
        "LMDM": 13,
        "LUDI": 14,
        "LUC": 15,
        "LDVC": 16,
        "LLR": 17,
        "LUD": 18,
        "LDVD": 19,
        "LDLF": 20,
        "LRN": 21,
        "LEXD": 22,
        "LNC": 99,
    }
    df_alignment_nuances = pd.DataFrame.from_dict(
        alignment_nuances, orient="index", columns=["Value"]
    )
    df_alignment_nuances.to_json(FOLDER_OUT + "vote_alignment_nuances.json")
    gdf_paris_voting_stations = gpd.read_file(
        FOLDER_IN + "votingparis_geometry_2020.geojson"
    )
    gdf_paris_vote = gdf_paris_voting_stations.merge(df_paris_vote, on="id_bv")
    df_iris_pop = pd.read_csv(
        FOLDER_IN + "IRIS_population_2021/base-ic-evol-struct-pop-2021.CSV",
        delimiter=";",
        low_memory=False,
    )
    df_iris_pop = df_iris_pop.rename({"IRIS": "CODE_IRIS"}, axis=1)
    gdf_iris = gpd.read_file(
        FOLDER_IN
        + "IRIS_geometry_2021/IRIS-GE/1_DONNEES_LIVRAISON_2021-06-00135/IRIS-GE_2-0_SHP_LAMB93_FXX-2021/IRIS_GE.SHP"
    )
    gdf_iris = gdf_iris.to_crs(epsg=4326)
    gdf_paris_iris = gpd.sjoin(
        gdf_iris, gdf_paris_vote, how="left", predicate="intersects"
    )
    gdf_paris_iris = gdf_paris_iris[gdf_paris_iris["index_right"].notna()][
        ["CODE_IRIS", "geometry"]
    ]
    gdf_paris_iris = gdf_paris_iris.drop_duplicates()
    gdf_paris_iris_pop = gdf_paris_iris.merge(df_iris_pop, on="CODE_IRIS")
    gdf_paris_iris_pop = gdf_paris_iris_pop.to_crs(
        gdf_paris_iris_pop.estimate_utm_crs()
    )
    gdf_paris_iris_pop["pop_density"] = gdf_paris_iris_pop.apply(
        lambda df: df.P21_POP / (df.geometry.area / 10**6), axis=1
    )
    gdf_paris_iris_pop = gdf_paris_iris_pop.to_crs(epsg=4326)
    gdf_paris_iris_pop.to_file(FOLDER_OUT + "paris_pop_iris.gpkg")
    gdf_paris_vote_list = gpd.GeoDataFrame(
        gdf_paris_vote.rename(candidates, axis=1)
        .T.groupby(level=0, by=set(nuances))
        .sum()
        .T.drop(
            [
                "ANNEE",
                "DATE",
                "SCRUTIN",
                "TOUR",
                "created_date",
                "created_user",
                "geo_point_2d",
                "last_edited_date",
                "last_edited_user",
                "num_bv",
            ],
            axis=1,
        ),
        crs="epsg:4326",
    )
    gdf_paris_vote_list.to_file(FOLDER_OUT + "paris_vote_list.gpkg")


if __name__ == "__main__":
    main()
