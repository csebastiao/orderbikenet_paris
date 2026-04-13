"""Get the data from the voting census area to the IRIS areas. Using functions adapted from https://github.com/NERDSITU/superblockify"""


from functools import partial
from multiprocessing import Pool
import geopandas as gpd
import shapely
import numpy as np
import tqdm


FOLDEROOTS = "./data/processed/paris_official_data/"
MET_LIST = [
    "LUD_share",
    "LUG_share",
]
BUSINESSES_TO_COUNT = [
    "Alimentaire",
    "Grand magasin",
    "Hôtel",
    "Non Alimentaire",
    "Restauration",
    "Service commercial",
]


def main():
    gdf_vote = gpd.read_file(FOLDEROOTS + "paris_vote_list_2020.gpkg")
    gdf_iris = gpd.read_file(FOLDEROOTS + "paris_dem_iris_2021_condensed.gpkg")
    gdf_apur = gpd.read_file(FOLDEROOTS + "paris_businesses_apur_2020.gpkg")
    gdf_iris = gdf_iris.to_crs(gdf_vote.crs)
    # Add values from gdf_vote
    for met in MET_LIST:
        gdf_iris = transfer_values(gdf_iris, gdf_vote, met, count=False, batch_size=600)
    # Add values from gdf_apur
    gdf_apur = gdf_apur[
        gdf_apur["LIBELLE_REGROUPEMENT_8_POSTES"].isin(BUSINESSES_TO_COUNT)
    ]
    gdf_iris_joined = gdf_iris.sjoin(gdf_apur)
    gdf_iris_joined_res = gdf_iris_joined.groupby(
        [gdf_iris_joined.index, "LIBELLE_REGROUPEMENT_8_POSTES"]
    )["REGROUPEMENT_8_POSTES"].count()
    gdf_iris_joined_res = gdf_iris_joined_res.reset_index(level=1)
    gdf_iris = gdf_iris.to_crs(gdf_iris.estimate_utm_crs())
    for bus in BUSINESSES_TO_COUNT:
        gdf_iris[bus] = 0
        gdf_filtered = gdf_iris_joined_res[
            gdf_iris_joined_res["LIBELLE_REGROUPEMENT_8_POSTES"] == bus
        ]["REGROUPEMENT_8_POSTES"]
        gdf_iris.loc[list(set(gdf_filtered.index)), bus] = gdf_filtered.values
        gdf_iris[bus + "_density"] = gdf_iris[bus] / (gdf_iris.geometry.area / 10**6)
    gdf_iris = gdf_iris.to_crs(epsg=4326)
    gdf_iris.to_file(FOLDEROOTS + "paris_dem_iris_2021_condensed_enriched.gpkg")


def transfer_values(gdf_to, gdf_from, metric_name, count=True, batch_size=10000):
    """
    Put the metric metric_name values from gdf_from to gdf_to, relative to the intersection of their polygons.

    Args:
        gdf_to (geopandas.GeoDataFrame): polygons to transfer data to.
        gdf_from (geopandas.GeoDataFrame): polygons to transfer data from.
        count (bool, optional): If True, consider the values as a count, else is a share. Defaults to True.
        batch_size (int, optional): Size of batches for multiprocessing. Defaults to 10000.

    Returns:
        geopandas.GeoDataFrame: gdf_to with the transferred data.
    """
    gdf_from_index = shapely.STRtree(gdf_from.geometry)
    gdf_to[metric_name] = 0.0
    batch_size = int(min(batch_size, len(gdf_to)))
    with Pool() as pool:
        slices = (
            slice(n_batch * batch_size, min((n_batch + 1) * batch_size, len(gdf_to)))
            for n_batch in range(0, len(gdf_to) // batch_size + 1)
        )

        value_sums = list(
            tqdm.tqdm(
                pool.imap_unordered(
                    partial(
                        _metric_fraction_list_sliced,
                        gdf_from["geometry"].values,
                        gdf_from[metric_name].values,
                        gdf_from_index,
                        gdf_to["geometry"].values,
                        count=count,
                    ),
                    slices,
                ),
                desc=f"Transferring values for metric {metric_name}",
                total=len(gdf_from) // batch_size + 1,
                unit="Cells",
                unit_scale=batch_size,
                unit_divisor=batch_size,
            )
        )
        # write the results to the dataframe
        for _, (cell_slice, value) in enumerate(value_sums):
            gdf_to.loc[gdf_to.index[cell_slice], metric_name] = value
    return gdf_to


# Marked as `no cover` as it is tested, but as a forked process with `multiprocessing`
def metric_fraction(
    polygon_from, metric_value, polygon_to, count=True
):  # pragma: no cover
    """Function returns fractional population count between polygon_to and
    polygon_from.

    Parameters
    ----------
    polygon_from : shapely.geometry.Polygon
        Polygon to transfer value from.
    metric_value : float
        Metric value of polygon_from.
    polygon_to : shapely.geometry.Polygon
        Polygon to transfer value to.
    count : bool, optional
        If True, consider the values as a count, else is a share. Defaults to True.

    Returns
    -------
    float
        Fractional value count between polygon_to and polygon_from.
    """
    intersection = polygon_to.intersection(polygon_from)
    if count:
        return metric_value * intersection.area / polygon_from.area
    return metric_value * intersection.area / polygon_to.area


def _metric_fraction_list(
    polygons_from,
    metric_values,
    overlap_index_pairs,
    polygons_to,
    count=True,
):  # pragma: no cover
    """Function returns population count for each road cell in polygons_to

    Parameters
    ----------
    polygons_from : list of shapely.geometry.Polygon
        List of polygons to transfer value from.
    metric_values : list of float
        List of metric values.
    overlap_index_pairs : ndarray with shape (2, n)
        Array of indices of overlapping road cells and cells.
        The first row contains the indices of the road cells, and the second row
        contains the indices of the cells.
    polygons_to : list of shapely.geometry.Polygon
        List of polygons to transfer value to.
    count : bool, optional
        If True, consider the values as a count, else is a share. Defaults to True.

    Returns
    -------
    ndarray with shape (n,)
        Array of population counts for each road cell in polygons_to.
    """
    value = np.zeros(len(polygons_to))
    for road_cell_idx, pop_cell_idx in overlap_index_pairs:
        value[road_cell_idx] += metric_fraction(
            polygons_from[pop_cell_idx],
            metric_values[pop_cell_idx],
            polygons_to[road_cell_idx],
            count=count,
        )
    return value


def _metric_fraction_list_sliced(
    polygons_from,
    metric_values,
    polygons_to_index,
    polygons_to,
    slice_n,
    count=True,
):  # pragma: no cover
    """Function for the parallelization of _population_fraction_list.

    Works like :func:`_population_fraction_list`, but takes all the road cells
    and only determines the population for the road cells in slice_n.

    Parameters
    ----------
    polygons_from : list of shapely.geometry.Polygon
        List of polygons to transfer value from.
    metric_values : list of float
        List of metric values of polygons_from.
    polygons_to_index : shapely.strtree.STRtree
        STRtree index of polygons_from.
    polygons_to : list of shapely.geometry.Polygon
        List of polygons to transfer value to.
    slice_n : slice
        Slice of polygons_to to determine the metric values for.
    count : bool, optional
        If True, consider the values as a count, else is a share. Defaults to True.

    Returns
    -------
    slice, ndarray with shape (n,)
        Slice of road cells and array of population counts for each road cell in
        polygons_to[slice_n].
    """
    return slice_n, _metric_fraction_list(
        polygons_from,
        metric_values,
        polygons_to_index.query(polygons_to[slice_n], predicate="intersects").T,
        polygons_to[slice_n],
        count=count,
    )


if __name__ == "__main__":
    main()
