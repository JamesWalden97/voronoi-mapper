from shapely.geometry import Polygon
from voronoi_mapper.geojson import (
    load_mask_geojson,
    load_points_and_features_from_geojson,
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
