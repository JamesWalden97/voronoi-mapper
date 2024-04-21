import json
from pdb import set_trace

import numpy as np
import pytest
from scipy.spatial import Voronoi
from shapely import Polygon, unary_union
from voronoi_mapper.models import Edges
from voronoi_mapper.voronoi import (
    _load_geojson_file,
    get_line_segments_from_voronoi,
    get_polygons_from_voronoi,
    load_mask_geojson,
    load_points_and_features_from_geojson,
)


def test_get_line_segments_from_voronoi(mock_voronoi, mock_bounding_box):
    segments, bounding_box_intersections = get_line_segments_from_voronoi(
        mock_voronoi, mock_bounding_box
    )

    expected_segments = [
        [[-0.5, 1.5], [2.5, 1.5]],
        [[-0.5, 1.5], [10, -9.0]],
        [[-0.5, 1.5], [-10, 6.25]],
        [[2.5, 1.5], [-6.0, 10]],
        [[2.5, 1.5], [10, -2.25]],
    ]

    segments = [list([list(y) for y in x]) for x in segments]

    assert all(segment in expected_segments for segment in segments)
    assert len(segments) > 0  # Assuming at least one segment is created
    assert isinstance(segments, list)
    assert isinstance(bounding_box_intersections, dict)
    assert all(
        edge in bounding_box_intersections
        for edge in [
            Edges.top.value,
            Edges.right.value,
            Edges.bottom.value,
            Edges.left.value,
        ]
    )


@pytest.fixture
def expected_test_geojson_content():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Severn Bridge parkrun"},
                "geometry": {"coordinates": [-2.6, 51.6], "type": "Point"},
                "id": 0,
            }
        ],
    }


@pytest.fixture
def sample_geojson_file_path():
    return "./tests/data/test_geojson_file.geojson"


def test_load_geojson_file(sample_geojson_file_path, expected_test_geojson_content):
    assert sorted(expected_test_geojson_content) == sorted(
        _load_geojson_file(sample_geojson_file_path)
    )


def test_load_points_and_features_from_geojson(
    sample_geojson_file_path, expected_test_geojson_content
):
    points, features = load_points_and_features_from_geojson(
        geojson_path=sample_geojson_file_path
    )

    expected_points = [[-2.6, 51.6]]
    expected_features = expected_test_geojson_content["features"]

    assert all(point in expected_points for point in points)
    assert sorted(features[0]) == sorted(expected_features[0])


def test_load_mask_geojson():
    expected_polygon = Polygon(
        [[3, 1], [3, 5], [4, 5], [4, 7], [7, 7], [7, 2], [5, 2], [5, 1], [3, 1]]
    )

    mask = load_mask_geojson(
        geojson_path="./tests/data/test_geojson_polygons_file.geojson"
    )

    assert expected_polygon.equals(mask)


def test_get_polygons_from_voronoi(
    mock_voronoi, mock_bounding_box, mock_expected_polygons
):
    polygon_generator = get_polygons_from_voronoi(
        voronoi=mock_voronoi, bounding_box=mock_bounding_box
    )

    unified_polygons = unary_union([polygon for polygon in polygon_generator])
    expected_unified_polygon = unary_union(mock_expected_polygons)

    assert unified_polygons.equals(expected_unified_polygon)


# def test_match_point_features_to_polygons(mock_points_as_features, mock_expected_polygons):
#     matched_polygons_and_features = match_point_features_to_polygons(
#         polygons=mock_expected_polygons, features=mock_points_as_features
#     )

#     expected_matches = zip()

#     assert
