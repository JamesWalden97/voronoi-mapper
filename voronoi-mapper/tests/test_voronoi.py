from pdb import set_trace

import geopandas as gpd
import pytest
from shapely import unary_union
from shapely.geometry import Polygon
from shapely.ops import shape
from voronoi_mapper.models import Edges
from voronoi_mapper.voronoi import (
    create_geodataframe_from_polygons_and_features,
    get_line_segments_from_voronoi,
    get_polygons_from_voronoi,
    match_point_features_to_polygons,
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


def test_get_polygons_from_voronoi(
    mock_voronoi, mock_bounding_box, mock_expected_polygons
):
    polygon_generator = get_polygons_from_voronoi(
        voronoi=mock_voronoi, bounding_box=mock_bounding_box
    )

    unified_polygons = unary_union([polygon for polygon in polygon_generator])
    expected_unified_polygon = unary_union(mock_expected_polygons)

    assert unified_polygons.equals(expected_unified_polygon)


def test_point_inside_polygon():
    polygon = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    feature = {"geometry": {"type": "Point", "coordinates": (1, 1)}}
    result = match_point_features_to_polygons([polygon], [feature])
    assert len(result) == 1
    assert polygon.equals(result[0][0])
    assert result[0][1] == feature


def test_point_outside_polygon():
    polygon = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    feature = {"geometry": {"type": "Point", "coordinates": (3, 3)}}
    result = match_point_features_to_polygons([polygon], [feature])
    assert len(result) == 0


def test_multiple_points():
    polygons = [
        Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
        Polygon([(3, 3), (5, 3), (5, 5), (3, 5)]),
    ]
    features = [
        {"geometry": {"type": "Point", "coordinates": (1, 1)}},
        {"geometry": {"type": "Point", "coordinates": (4, 4)}},
        {"geometry": {"type": "Point", "coordinates": (6, 6)}},
    ]
    result = match_point_features_to_polygons(polygons, features)
    assert len(result) == 2
    assert result[0][0].equals(polygons[0])
    assert result[1][0].equals(polygons[1])


@pytest.mark.parametrize(
    "polygons,features,expected_geodataframe",
    [
        (
            [
                Polygon(
                    [
                        (-0.5, 1.5),
                        (2.5, 1.5),
                        (10.0, -2.25),
                        (10.0, -9.0),
                        (-0.5, 1.5),
                    ]
                )
            ],
            [
                {
                    "type": "Feature",
                    "properties": {"id": 0},
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                }
            ],
            gpd.GeoDataFrame(
                {
                    "geometry": [
                        shape(
                            {
                                "type": "Polygon",
                                "coordinates": [
                                    [
                                        [-0.5, 1.5],
                                        [2.5, 1.5],
                                        [10.0, -2.25],
                                        [10.0, -9.0],
                                        [-0.5, 1.5],
                                    ]
                                ],
                            }
                        )
                    ],
                    "id": 0,
                }
            ),
        )
    ],
)
def test_create_geodataframe_from_polygons_and_features(
    polygons, features, expected_geodataframe
):
    gdf = create_geodataframe_from_polygons_and_features(
        polygons=polygons, features=features
    )

    assert gdf.equals(expected_geodataframe)
