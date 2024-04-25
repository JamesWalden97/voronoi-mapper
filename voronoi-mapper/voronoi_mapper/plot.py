from pathlib import Path
from pdb import set_trace

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.axes import Axes
from scipy.spatial import Voronoi, voronoi_plot_2d
from shapely.geometry import MultiPolygon, Polygon
from voronoi_mapper.models import BoundingBox


def plot_voronoi(
    voronoi: Voronoi,
    save_path: Path | str,
    bounding_box: BoundingBox | None = None,
    boundary: Polygon | MultiPolygon | None = None,
    show: bool = False,
):
    _, ax = plt.subplots(figsize=(8, 6))
    ax: Axes = ax

    # gridlines
    ax.grid(which="major", color="#BBBBBB", linewidth=0.6)
    ax.grid(which="minor", color="#CCCCCC", linestyle=":", linewidth=0.35)
    ax.minorticks_on()

    voronoi_plot_2d(
        voronoi,
        ax=ax,
        show_vertices=True,
        line_colors="blue",
        line_width=2,
        point_size=5,
    )

    # bounding box
    if bounding_box is not None:
        width = bounding_box.xmax - bounding_box.xmin
        height = bounding_box.ymax - bounding_box.ymin
        rectangle = patches.Rectangle(
            (bounding_box.xmin, bounding_box.ymin),
            width,
            height,
            linewidth=1,
            edgecolor="#39fc03",
            facecolor="none",
        )
        ax.add_patch(rectangle)

        ax.set_xlim((bounding_box.xmin - 1, bounding_box.xmax + 1))
        ax.set_ylim((bounding_box.ymin - 1, bounding_box.ymax + 1))

    # boundary
    if boundary is not None:
        if boundary.geom_type == "Polygon":
            plot_polygon(ax, boundary)

        elif boundary.geom_type == "MultiPolygon":
            for polygon in boundary.geoms:
                plot_polygon(ax, polygon)

    # titles
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Voronoi Diagram")

    plt.savefig(save_path)
    if show:
        plt.show()  # pragma: no cover


def plot_polygon(ax: Axes, polygon: Polygon):
    """
    Helper function to plot a single polygon.

    Parameters:
        ax (matplotlib axes): The axes on which to plot.
        polygon (Shapely Polygon): The polygon to plot.
    """
    x, y = polygon.exterior.xy
    ax.fill(x, y, alpha=0.5, color="orange")  # Fill the polygon with transparency
