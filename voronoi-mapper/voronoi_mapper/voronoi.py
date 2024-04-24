import json
from pathlib import Path
from pdb import set_trace
from typing import Generator

import geopandas as gpd
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import LineString, Polygon
from shapely.ops import polygonize
from voronoi_mapper.geojson import (
    load_mask_geojson,
    load_points_and_features_from_geojson,
)
from voronoi_mapper.geometry import (
    clip_polygons_to_mask,
    get_bounding_segments,
    get_intersection_with_bounding_box,
    match_point_features_to_polygons,
)
from voronoi_mapper.models import BoundingBox, Edges
from voronoi_mapper.plot import plot_voronoi


def _remove_coordinate_duplicates_from_list(coordinate_list: list[list[float]]):
    """Remove duplicate coordinates from list."""
    unique_tuples = set(tuple(item) for item in coordinate_list)
    return [list(item) for item in unique_tuples]


def _remove_segment_duplicates_from_list(segments: list[list[list[float]]]):
    """Remove duplicate segments from list.

    Segment AB is treated as different to segment BA.
    """
    unique_segments = set(tuple(map(tuple, segment)) for segment in segments)
    return [list(map(list, segment)) for segment in unique_segments]


def get_line_segments_from_voronoi(
    voronoi: Voronoi, bounding_box: BoundingBox
) -> tuple[list[list[float]], dict[str, list[list[float]]]]:
    """Get the list of line segments within a bounding box from a scipy Voronoi object."""
    center = voronoi.points.mean(axis=0)
    segments: list[tuple[float, float]] = []
    bounding_box_intersections: dict[str, list[list[float]]] = {
        Edges.top.value: [],
        Edges.right.value: [],
        Edges.bottom.value: [],
        Edges.left.value: [],
    }
    # Essentially a copy of the code from voronoi_plot_2d but with extension of
    # infinity edges to a bounding box.
    for pointidx, simplex in zip(voronoi.ridge_points, voronoi.ridge_vertices):
        simplex = np.asarray(simplex)
        if np.all(simplex >= 0):
            segments.append(voronoi.vertices[simplex].tolist())
            continue

        i = simplex[simplex >= 0][0]

        t = voronoi.points[pointidx[1]] - voronoi.points[pointidx[0]]
        t /= np.linalg.norm(t)
        n = np.array([-t[1], t[0]])

        midpoint = voronoi.points[pointidx].mean(axis=0)
        direction = np.sign(np.dot(midpoint - center, n)) * n

        # intersection with bounding box
        intersection = get_intersection_with_bounding_box(
            coordinates=(voronoi.vertices[i], voronoi.vertices[i] + direction),
            bounding_box=bounding_box,
        )

        segments.append([voronoi.vertices[i], intersection.coordinates])

        bounding_box_intersections[intersection.edge.value].append(
            intersection.coordinates
        )

    segments = _remove_segment_duplicates_from_list(segments=segments)

    for k, v in bounding_box_intersections.items():
        bounding_box_intersections[k] = _remove_coordinate_duplicates_from_list(
            coordinate_list=v
        )

    return segments, bounding_box_intersections


def get_polygons_from_voronoi(
    voronoi: Voronoi, bounding_box: BoundingBox
) -> Generator[Polygon, None, None]:
    segments, bounding_box_intersections = get_line_segments_from_voronoi(
        voronoi=voronoi, bounding_box=bounding_box
    )

    bounding_segments = get_bounding_segments(
        bounding_box=bounding_box, bounding_box_intersections=bounding_box_intersections
    )

    segments.extend(bounding_segments)

    segments = [LineString(coordinates=segment) for segment in segments]

    return polygonize(segments)


def create_geodataframe_from_polygons_and_features(
    matched_polygons_and_features: list[tuple[Polygon, dict]]
) -> gpd.GeoDataFrame:
    gdf = gpd.GeoDataFrame(
        [
            {"geometry": matched_polygon, **matched_feature["properties"]}
            for matched_polygon, matched_feature in matched_polygons_and_features
        ]
    )
    gdf = gdf.set_geometry("geometry")
    return gdf


def get_bounding_box(voronoi: Voronoi) -> BoundingBox:
    return BoundingBox(
        xmin=-90,
        xmax=90,
        ymin=-90,
        ymax=90,
    )


def voronoi_map(
    features_file_path: Path | str,
    boundary_file_path: Path | str,
    bounding_box: BoundingBox | None = None,
    save_path: Path | str | None = None,
):
    points, features = load_points_and_features_from_geojson(
        geojson_path=features_file_path
    )
    mask = load_mask_geojson(geojson_path=boundary_file_path)

    voronoi = Voronoi(points)

    bounding_box = (
        get_bounding_box(voronoi=voronoi) if bounding_box is None else bounding_box
    )

    polygons = get_polygons_from_voronoi(voronoi=voronoi, bounding_box=bounding_box)

    matched_points = match_point_features_to_polygons(
        polygons=polygons, features=features
    )

    gdf = create_geodataframe_from_polygons_and_features(
        matched_polygons_and_features=matched_points
    )

    gdf = clip_polygons_to_mask(gdf=gdf, mask=mask)

    if save_path is not None:
        gdf.to_file(save_path, driver="GeoJSON")


if __name__ == "__main__":
    POINTS_GEOJSON_PATH = "./_data/points.geojson"
    BOUNDARY_GEOJSON_PATH = "./_data/wales.geojson"
    GEOJSON_SAVE_PATH = "./_data/wales_parkrun_polygons.geojson"

    voronoi_map(
        features_file_path=POINTS_GEOJSON_PATH,
        boundary_file_path=BOUNDARY_GEOJSON_PATH,
        save_path=GEOJSON_SAVE_PATH,
    )
