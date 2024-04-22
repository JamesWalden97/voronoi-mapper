from os import PathLike
from pdb import set_trace

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from scipy.spatial import Voronoi, voronoi_plot_2d
from shapely.ops import polygonize
from voronoi_mapper.models import BoundingBox


def plot_voronoi(voronoi: Voronoi, bounding_box: BoundingBox, save_path: PathLike):
    _, ax = plt.subplots(figsize=(8, 6))
    ax: Axes = ax
    voronoi_plot_2d(vor=voronoi, ax=ax)

    ax.set_xlim((bounding_box.xmin, bounding_box.xmax))
    ax.set_ylim((bounding_box.ymin, bounding_box.ymax))

    ax.grid(which="major", color="#BBBBBB", linewidth=0.8)
    ax.grid(which="minor", color="#CCCCCC", linestyle=":", linewidth=0.5)
    ax.minorticks_on()
    plt.savefig(save_path)


def plot_polygons(segments):
    for segment in segments:
        plt.plot(*segment.xy)

    for polygon in polygonize(segments):
        x, y = polygon.exterior.xy
        plt.plot(x, y)

    plt.savefig("./etl/data/plots/polygon_plot.png")


def plot_dataframe_polygons(gdf: gpd.GeoDataFrame):
    geometries: list = gdf["geometry"].to_list()

    fig, ax = plt.subplots(figsize=(10, 10))

    for polygon in geometries:
        if polygon.geom_type == "Polygon":
            plt.plot(*polygon.exterior.xy, color="yellow")
            continue
        for geom in polygon.geoms:
            plt.plot(*geom.exterior.xy, color="red")

    plt.savefig("./etl/data/plots/final_vornoi.png")
    plt.show()
