from pdb import set_trace

import geopandas as gpd
import pytest
from shapely.geometry import MultiPolygon, Polygon
from voronoi_mapper.geometry import (
    calculate_gradient,
    check_point_is_within,
    clip_polygons_to_mask,
    get_bounding_segments,
    get_intersection_with_bounding_box,
    handle_straight_lines,
)
from voronoi_mapper.models import (
    BoundingBox,
    Edges,
    Intersection,
    IntersectionException,
)


@pytest.mark.parametrize(
    "point_a,point_b,expected_output",
    [
        ([1, 1], [2, 7], 6),
        ([2, 5], [-1, 1], 1.33),
    ],
)
def test_gradient(point_a, point_b, expected_output):
    m_grad = calculate_gradient(point_a=point_a, point_b=point_b)
    assert round(m_grad, 2) == expected_output


@pytest.mark.parametrize(
    "point_a,point_b,expected_output",
    [([1, 1], [2, 1], 0), ([1, 1], [1, 2], None)],
)
def test_gradient_h_v(point_a, point_b, expected_output):
    assert expected_output == calculate_gradient(point_a=point_a, point_b=point_b)


@pytest.mark.parametrize(
    "point_a,point_b,point_c,expected_output",
    [
        ([1, 1], [2, 2], [3, 3], True),
        ([2, 2], [1, 1], [3, 3], False),
    ],
)
def test_check_point_is_within(
    point_a: list[float], point_b: list[float], point_c: list[float], expected_output
):
    assert expected_output == check_point_is_within(
        point_a=point_a, point_b=point_b, point_c=point_c
    )


@pytest.mark.parametrize(
    "coordinates,bounding_box,expected_output",
    [
        (
            [[1, 0], [2, 2]],
            BoundingBox(xmin=0, xmax=5, ymin=0, ymax=5),
            Intersection(coordinates=(3.5, 5), edge=Edges.top),
        ),
        (
            [[0, 3], [1, 2]],
            BoundingBox(xmin=0, xmax=5, ymin=0, ymax=5),
            Intersection(coordinates=(3, 0), edge=Edges.bottom),
        ),
        (
            [[2, 3], [1, 2]],
            BoundingBox(xmin=0, xmax=5, ymin=0, ymax=5),
            Intersection(coordinates=(0, 1), edge=Edges.left),
        ),
        (
            [[3, 4], [4, 3]],
            BoundingBox(xmin=0, xmax=5, ymin=0, ymax=5),
            Intersection(coordinates=(5, 2), edge=Edges.right),
        ),
        (
            [[2, 3], [4, 3]],
            BoundingBox(xmin=0, xmax=5, ymin=0, ymax=5),
            Intersection(coordinates=(5, 3), edge=Edges.right),
        ),
        (
            [[4, 3], [2, 3]],
            BoundingBox(xmin=0, xmax=5, ymin=0, ymax=5),
            Intersection(coordinates=(0, 3), edge=Edges.left),
        ),
        (
            [[2, 3], [2, 4]],
            BoundingBox(xmin=0, xmax=5, ymin=0, ymax=5),
            Intersection(coordinates=(2, 5), edge=Edges.top),
        ),
        (
            [[4, 3], [4, 1]],
            BoundingBox(xmin=0, xmax=5, ymin=0, ymax=5),
            Intersection(coordinates=(4, 0), edge=Edges.bottom),
        ),
    ],
)
def test_get_intersection_with_bounding_box(
    coordinates: list[list[float]],
    bounding_box: BoundingBox,
    expected_output: Intersection,
):
    assert expected_output == get_intersection_with_bounding_box(
        coordinates=coordinates, bounding_box=bounding_box
    )


@pytest.mark.parametrize(
    "coordinates,bounding_box",
    [
        (
            [[1, 0], [4, 4]],
            BoundingBox(xmin=0, xmax=2, ymin=0, ymax=2),
        ),
    ],
)
def test_get_intersection_with_bounding_box_exception(
    coordinates: list[list[float]],
    bounding_box: BoundingBox,
):
    with pytest.raises(IntersectionException) as exc_info:
        get_intersection_with_bounding_box(
            coordinates=coordinates, bounding_box=bounding_box
        )
    assert "No intersections found" in str(exc_info.value)


def test_get_bounding_segments(mock_bounding_box, mock_bounding_box_intersections):
    bounding_segments = get_bounding_segments(
        bounding_box=mock_bounding_box,
        bounding_box_intersections=mock_bounding_box_intersections,
    )

    expected_bounding_segments = [
        ((-10, 10), [-6.0, 10]),
        ([-6.0, 10], (10, 10)),
        ((10, -10), [10, -9.0]),
        ([10, -9.0], [10, -2.25]),
        ([10, -2.25], (10, 10)),
        ((-10, -10), (10, -10)),
        ((-10, -10), [-10, 6.25]),
        ([-10, 6.25], (-10, 10)),
    ]

    assert all(segment in expected_bounding_segments for segment in bounding_segments)


def test_clip_polygons_within_mask(mock_geo_dataframe, mock_mask):
    clipped = clip_polygons_to_mask(mock_geo_dataframe, mock_mask)
    assert len(clipped) == 1
    assert clipped.geometry.iloc[0].equals(Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]))


@pytest.mark.parametrize(
    "geo_dataframe,mask",
    [
        (
            gpd.GeoDataFrame(
                {
                    "geometry": [
                        Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
                        Polygon([(4, 3), (5, 3), (5, 5), (3, 5)]),
                    ]
                }
            ),
            MultiPolygon([Polygon([(10, 10), (12, 10), (12, 12), (10, 12)])]),
        ),
        (
            gpd.GeoDataFrame(
                {
                    "geometry": [
                        Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
                        Polygon([(4, 3), (5, 3), (5, 5), (3, 5)]),
                    ]
                }
            ),
            MultiPolygon(),
        ),
        (
            gpd.GeoDataFrame(columns=["geometry"], geometry="geometry"),
            MultiPolygon([Polygon([(10, 10), (12, 10), (12, 12), (10, 12)])]),
        ),
    ],
)
def test_clip_polygons_outside_mask(geo_dataframe, mask):
    clipped = clip_polygons_to_mask(geo_dataframe, mask)
    assert clipped.empty


@pytest.mark.parametrize(
    "point_a,point_b,gradient,bounding_box,expected_intersection",
    [
        (
            [1, 2],
            [3, 2],
            0,
            BoundingBox(xmin=0, xmax=4, ymin=0, ymax=4),
            Intersection(coordinates=(4, 2), edge=Edges.right),
        ),
        (
            [1, 1],
            [1, 3],
            None,
            BoundingBox(xmin=0, xmax=4, ymin=0, ymax=4),
            Intersection(coordinates=(1, 4), edge=Edges.top),
        ),
        (
            [3, 2],
            [1, 2],
            0,
            BoundingBox(xmin=0, xmax=4, ymin=0, ymax=4),
            Intersection(coordinates=(0, 2), edge=Edges.left),
        ),
        (
            [1, 3],
            [1, 1],
            None,
            BoundingBox(xmin=0, xmax=4, ymin=0, ymax=4),
            Intersection(coordinates=(1, 0), edge=Edges.bottom),
        ),
    ],
)
def test_handle_straight_lines(
    point_a, point_b, gradient, bounding_box, expected_intersection
):
    actual_intersection = handle_straight_lines(
        point_a, point_b, gradient, bounding_box
    )

    assert actual_intersection.coordinates == expected_intersection.coordinates
    assert actual_intersection.edge == expected_intersection.edge
