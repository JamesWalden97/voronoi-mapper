import pytest
from voronoi_mapper.geometry import (
    check_point_is_within,
    get_bounding_segments,
    get_intersection_with_bounding_box,
    gradient,
    match_point_features_to_polygons,
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
    m_grad = gradient(point_a=point_a, point_b=point_b)
    assert round(m_grad, 2) == expected_output


@pytest.mark.parametrize(
    "point_a,point_b,expected_output",
    [([1, 1], [2, 1], 0), ([1, 1], [1, 2], None)],
)
def test_gradient_h_v(point_a, point_b, expected_output):
    assert expected_output == gradient(point_a=point_a, point_b=point_b)


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
        assert "No intersections" in exc_info


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
