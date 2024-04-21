import json
from pdb import set_trace
from typing import Generator

import geopandas as gpd
import numpy as np
import shapely as shp
from scipy.spatial import Voronoi
from shapely.geometry import LineString, MultiPolygon, Polygon
from shapely.ops import polygonize
from voronoi_mapper.geojson import (
    load_mask_geojson,
    load_points_and_features_from_geojson,
)
from voronoi_mapper.geometry import (
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
    polygons: list[Polygon], features: list
) -> gpd.GeoDataFrame:
    matched_polygons_and_features = match_point_features_to_polygons(
        polygons=polygons, features=features
    )

    polygon_point_pairs = []
    for matched_polygon, matched_feature in matched_polygons_and_features:
        polygon_point_pairs.append(
            {"geometry": matched_polygon, **matched_feature["properties"]}
        )

    gdf = gpd.GeoDataFrame(polygon_point_pairs)
    gdf = gdf.set_geometry("geometry")
    return gdf


def clip_polygons_to_mask(
    gdf: gpd.GeoDataFrame, mask: MultiPolygon
) -> gpd.GeoDataFrame:
    return gdf.clip(mask=mask)


if __name__ == "__main__":
    POINTS_GEOJSON_PATH = "./etl/data/1_raw/wales_parkrun_points.geojson"
    BOUNDARY_GEOJSON_PATH = "./etl/data/countries/wales.geojson"
    DATAFRAME_SAVE_PATH = "./etl/data/1_raw/wales_parkrun_polygons.geojson"
    points, features = load_points_and_features_from_geojson(
        geojson_path=POINTS_GEOJSON_PATH
    )
    mask = load_mask_geojson(geojson_path=BOUNDARY_GEOJSON_PATH)

    bbox = BoundingBox(
        xmin=-25,
        xmax=25,
        ymin=5,
        ymax=10,
    )

    voronoi = Voronoi(points)
    plot_voronoi(voronoi=voronoi, bounding_box=bbox)

    polygons = get_polygons_from_voronoi(voronoi=voronoi, bounding_box=bbox)

    gdf = match_point_features_to_polygons(polygons=polygons, features=features)

    gdf = clip_polygons_to_mask(gdf=gdf, mask=mask)

    gdf.to_file(DATAFRAME_SAVE_PATH, driver="GeoJSON")
