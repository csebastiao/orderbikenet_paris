# -*- coding: utf-8 -*-
"""
Create paris demographics processed files from raw files.
"""

import os
import numpy as np
import pandas as pd
import shapely
from libpysal import weights
import geopandas as gpd
import osmnx as ox

FOLDER_IN = "./data/raw/official_data/"
FOLDER_OUT = "./data/processed/paris_official_data/"
BUFF_SIZE = 400
MET_LIST = [
    "median_income",
    "poverty_rate",
    "commuter_cyclist_share",
    "commuter_driver_share",
]
COLS_TO_DROP = [
    "NB_BLANC",
    "NB_EMARG",
    "NB_INSCR",
    "NB_NUL",
    "NB_PROCU",
    "NB_VOTANT",
    "NUM_CIRC",
    "NUM_QUARTIER",
    "id_bv",
    "st_area_shape",
    "st_perimeter_shape",
]
ALIGNMENT_NUANCES_2020 = {
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
ALIGNMENT_NUANCES_2026 = {
    "LEXG": 0,
    "LFI": 1,
    "LCOM": 2,
    "LSOC": 3,
    "LVEC": 4,
    "LUG": 5,
    "LDVG": 6,
    "LECO": 7,
    "LREG": 8,
    "LDIV": 9,
    "LREN": 10,
    "LMDM": 11,
    "LHOR": 12,
    "LUDI": 13,
    "LUC": 14,
    "LDVC": 15,
    "LLR": 16,
    "LUD": 17,
    "LDVD": 18,
    "LDSV": 19,
    "LUDR": 20,
    "LRN": 21,
    "LREC": 22,
    "LUXD": 23,
    "LEXD": 24,
}


def main():
    if not os.path.exists(FOLDER_OUT):
        os.makedirs(FOLDER_OUT)
    # Make voting results for 2020
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
    df_alignment_nuances = pd.DataFrame.from_dict(
        ALIGNMENT_NUANCES_2020, orient="index", columns=["Value"]
    )
    df_alignment_nuances.to_json(FOLDER_OUT + "vote_alignment_nuances_2020.json")
    df_alignment_nuances = pd.DataFrame.from_dict(
        ALIGNMENT_NUANCES_2026, orient="index", columns=["Value"]
    )
    df_alignment_nuances.to_json(FOLDER_OUT + "vote_alignment_nuances_2026.json")
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
    G = ox.load_graphml(
        "./data/processed/paris_simplified_results/paris_cleaned_multigraph.graphml"
    )
    edges = (
        ox.graph_to_gdfs(G, edges=True, nodes=False).buffer(BUFF_SIZE).to_crs(epsg=4326)
    )
    gdf_paris_iris = gdf_iris[
        gdf_iris.intersects(shapely.Polygon(edges.union_all().exterior))
    ]
    gdf_paris_iris = gdf_paris_iris[["CODE_IRIS", "geometry"]]
    gdf_paris_iris_pop = gdf_paris_iris.merge(df_iris_pop, on="CODE_IRIS")
    gdf_paris_iris_pop = gdf_paris_iris_pop.to_crs(
        gdf_paris_iris_pop.estimate_utm_crs()
    )
    gdf_paris_iris_pop["pop_density"] = gdf_paris_iris_pop.apply(
        lambda df: df.P21_POP / (df.geometry.area / 10**6), axis=1
    )
    gdf_paris_iris_pop = gdf_paris_iris_pop.to_crs(epsg=4326)
    df_iris_income = pd.read_csv(
        FOLDER_IN + "IRIS_income_2021/BASE_TD_FILO_IRIS_2021_DISP.csv",
        delimiter=";",
        low_memory=False,
    )
    df_iris_income = df_iris_income.rename({"IRIS": "CODE_IRIS"}, axis=1)
    gdf_paris_iris_pop_income = gdf_paris_iris_pop.merge(df_iris_income, on="CODE_IRIS")
    df_iris_activity = pd.read_csv(
        FOLDER_IN + "IRIS_activity_2021/base-ic-activite-residents-2021.CSV",
        delimiter=";",
        low_memory=False,
    )
    df_iris_activity = df_iris_activity.rename({"IRIS": "CODE_IRIS"}, axis=1)
    gdf_paris_iris_all = gdf_paris_iris_pop_income.merge(
        df_iris_activity, on="CODE_IRIS"
    )
    gdf_paris_iris_all.to_file(FOLDER_OUT + "paris_dem_iris_2021.gpkg")
    gdf_small = gdf_paris_iris_all[
        [
            "CODE_IRIS",
            "P21_POP",
            "pop_density",
            "C21_ACTOCC15P",
            "C21_ACTOCC15P_VELO",
            "C21_ACTOCC15P_VOIT",
            "DISP_MED21",
            "DISP_TP6021",
            "geometry",
        ]
    ]
    # TODO find way to remove settingwithcopywarning
    gdf_small["DISP_TP6021"] = gdf_small["DISP_TP6021"].apply(
        lambda x: np.nan if "n" in x else int(float(x.replace(",", ".")))
    )
    gdf_small["DISP_MED21"] = gdf_small["DISP_MED21"].apply(
        lambda x: np.nan if "n" in x else int(float(x.replace(",", ".")))
    )
    gdf_small["commuter_cyclist_share"] = (
        gdf_small.C21_ACTOCC15P_VELO / gdf_small.C21_ACTOCC15P
    )
    gdf_small["commuter_driver_share"] = (
        gdf_small.C21_ACTOCC15P_VOIT / gdf_small.C21_ACTOCC15P
    )
    gdf_small = gdf_small.rename(
        {
            "P21_POP": "population",
            "DISP_TP6021": "poverty_rate",
            "DISP_MED21": "median_income",
            "C21_ACTOCC15P": "active_population",
        },
        axis=1,
    )
    gdf_small = gdf_small.drop(["C21_ACTOCC15P_VELO", "C21_ACTOCC15P_VOIT"], axis=1)
    # Replace na values for columns in MET_LIST by the average values of the k nearest neighbors with values
    gdf_small_na = gdf_small[gdf_small["median_income"].isna()]
    gdf_small_notna = gdf_small[gdf_small["median_income"].notna()]
    change_dict = {met: {} for met in MET_LIST}
    for idx, row in gdf_small_na.iterrows():
        gdf_iris_temp = gdf_small_notna.copy()
        gdf_iris_temp.loc[-1] = row
        W = weights.KNN.from_dataframe(gdf_iris_temp, use_index=True, k=8)
        W.transform = "r"
        for met in MET_LIST:
            change_dict[met][idx] = weights.lag_spatial(
                W, gdf_iris_temp[met].fillna(0).values
            )[-1]
    for met in MET_LIST:
        gdf_small[met] = gdf_small[met].fillna(change_dict[met])
    gdf_small["median_income"] = gdf_small["median_income"].map(round)
    gdf_small["poverty_rate"] = gdf_small["poverty_rate"].map(round)
    gdf_small.to_file(FOLDER_OUT + "paris_dem_iris_2021_condensed.gpkg")
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
    for col in list(gdf_paris_vote_list.columns)[:16]:
        gdf_paris_vote_list[col] = gdf_paris_vote_list[col].map(float).map(int)
    agg_func = {}
    agg_func["NB_EXPRIM"] = "sum"
    all_2020_parties = list(ALIGNMENT_NUANCES_2020.keys())
    left_parties = []
    right_parties = []
    for col in list(gdf_paris_vote_list.columns)[:9]:
        if all_2020_parties.index(col) < 12:
            left_parties.append(col)
        elif all_2020_parties.index(col) >= 17:
            right_parties.append(col)
    gdf_paris_vote_list["Left_wing"] = gdf_paris_vote_list.apply(
        lambda df: sum([df[party_name] for party_name in left_parties]), axis=1
    )
    gdf_paris_vote_list["Right_wing"] = gdf_paris_vote_list.apply(
        lambda df: sum([df[party_name] for party_name in right_parties]), axis=1
    )
    agg_func["Left_wing"] = "sum"
    agg_func["Right_wing"] = "sum"
    for col in list(gdf_paris_vote_list.columns)[:9] + ["Left_wing", "Right_wing"]:
        gdf_paris_vote_list[col + "_share"] = (
            gdf_paris_vote_list[col] / gdf_paris_vote_list["NB_EXPRIM"]
        )
        agg_func[col] = "sum"
    rm = (
        gdf_paris_vote_list["Right_wing"].sum() / gdf_paris_vote_list["NB_EXPRIM"].sum()
    )
    lm = gdf_paris_vote_list["Left_wing"].sum() / gdf_paris_vote_list["NB_EXPRIM"].sum()
    vote_avg_ratio = rm - lm
    gdf_paris_vote_list["ratio_LR"] = (
        (gdf_paris_vote_list["Right_wing"] - gdf_paris_vote_list["Left_wing"])
        / gdf_paris_vote_list["NB_EXPRIM"]
    ) - vote_avg_ratio
    gdf_paris_vote_list = gdf_paris_vote_list.drop(COLS_TO_DROP, axis=1)
    gdf_paris_vote_list.to_file(FOLDER_OUT + "paris_vote_list_2020.gpkg")
    gdf_paris_vote_arr = gdf_paris_vote_list.dissolve(by="NUM_ARROND", aggfunc=agg_func)
    for col in list(gdf_paris_vote_list.columns)[:9] + ["Left_wing", "Right_wing"]:
        gdf_paris_vote_arr[col + "_share"] = (
            gdf_paris_vote_arr[col] / gdf_paris_vote_arr["NB_EXPRIM"]
        )
        agg_func[col] = "sum"
    rm = gdf_paris_vote_arr["Right_wing_share"].mean()
    lm = gdf_paris_vote_arr["Left_wing_share"].mean()
    vote_avg_ratio = rm - lm
    gdf_paris_vote_arr["ratio_LR"] = (
        (gdf_paris_vote_arr["Right_wing"] - gdf_paris_vote_arr["Left_wing"])
        / gdf_paris_vote_arr["NB_EXPRIM"]
    ) - vote_avg_ratio
    gdf_paris_vote_arr.to_file(FOLDER_OUT + "paris_vote_arr_2020.gpkg")
    gdf_businesses_apur = gpd.read_file(FOLDER_IN + "APUR_businesses_2020.geojson")
    gdf_businesses_apur.to_file(FOLDER_OUT + "paris_businesses_apur_2020.gpkg")
    # Make voting results for 2026
    df_fr = pd.read_csv(
        FOLDER_IN + "votingarr_values_2026/arrondissements_firstround_2026.csv",
        delimiter=";",
    )
    df_fr = df_fr[df_fr["Code département"] == 75]
    df_sr = pd.read_csv(
        FOLDER_IN + "votingarr_values_2026/arrondissements_secondround_2026.csv",
        delimiter=";",
    )
    df_sr = df_sr[df_sr["Code département"] == 75]
    df_all = pd.concat([df_sr, df_fr[~df_fr["Code BV"].isin(df_sr["Code BV"].values)]])
    gdf_sta = gpd.read_file(FOLDER_IN + "votingparis_geometry_2026.geojson")
    gdf_sta["Code BV"] = gdf_sta.apply(
        lambda df: int(str(df.arrondissement) + str(df.num_bv).zfill(2)), axis=1
    )
    gdf_vote_sta = gdf_sta.merge(df_all, on="Code BV")
    party_paris = {
        x
        for x in set.union(
            *[set(gdf_vote_sta[f"Nuance liste {i}"].values) for i in range(1, 12)]
        )
        if pd.notna(x)
    }
    gdf_cleaned = gdf_vote_sta.copy()
    for idx, row in gdf_vote_sta.iterrows():
        for i in range(1, 12):
            if pd.notna(row[f"Nuance liste {i}"]):
                gdf_cleaned.loc[idx, row[f"Nuance liste {i}"]] = row[f"Voix {i}"]
    gdf_cleaned = gdf_cleaned.fillna(0)
    for p in party_paris:
        gdf_cleaned[p + "_share"] = gdf_cleaned[p] / gdf_cleaned["Exprimés"]
    gdf_cleaned = gdf_cleaned[
        [
            "arrondissement",
            "num_bv",
            "geometry",
            "Code BV",
            "Votants",
            "Exprimés",
            "Inscrits",
            "Blancs",
            "Abstentions",
        ]
        + [p for p in party_paris]
        + [p + "_share" for p in party_paris]
    ]
    gdf_cleaned = gdf_cleaned.to_crs(gdf_paris_vote_list.crs)
    gdf_cleaned.to_file(FOLDER_OUT + "paris_vote_list_2026.gpkg")
    gdf_cleaned_arr = gdf_cleaned.dissolve(by="arrondissement")
    gdf_cleaned_arr.to_file(FOLDER_OUT + "paris_vote_arr_2026.gpkg")


if __name__ == "__main__":
    main()
