from shapely.geometry import Polygon, shape
from voronoi_mapper.models import (
    BoundingBox,
    Edges,
    Intersection,
    IntersectionException,
)


def gradient(point_a: list[float], point_b: list[float]) -> float:
    """Returns gradient from point A to point B.

    0 for horizontal, None for vertical.

    """
    dy = point_b[1] - point_a[1]
    dx = point_b[0] - point_a[0]
    if any(x == 0 for x in [dy, dx]):
        if dy == 0:
            # horizontal
            return 0
        # vertical
        return None
    return (dy) / (dx)


def check_point_is_within(
    point_a: list[float], point_b: list[float], point_c: list[float]
):
    """Checks if point_b is between point_a and point_c.

    Assumes they are colinear.
    """
    return (
        min(point_a[0], point_c[0]) <= point_b[0] <= max(point_a[0], point_c[0])
    ) and (min(point_a[1], point_c[1]) <= point_b[1] <= max(point_a[1], point_c[1]))


def get_intersection_with_bounding_box(
    coordinates: tuple[list[float]], bounding_box: BoundingBox
) -> Intersection:
    """Calculates intersection coordinates of line with bounding box, from point_a to point_b."""
    point_a, point_b = coordinates
    m_grad = gradient(point_a=point_a, point_b=point_b)

    if m_grad in [0, None]:
        intersection: Intersection
        if m_grad == 0:
            # horizontal
            left_to_right = (point_b[0] - point_a[0]) > 0
            return Intersection(
                coordinates=(
                    bounding_box.xmax if left_to_right else bounding_box.xmin,
                    point_a[1],
                ),
                edge=Edges.right if left_to_right else Edges.left,
            )
        # vertical
        bottom_to_top = (point_b[1] - point_a[1]) > 0
        return Intersection(
            coordinates=(
                point_b[0],
                bounding_box.ymax if bottom_to_top else bounding_box.ymin,
            ),
            edge=Edges.top if bottom_to_top else Edges.bottom,
        )

    intersections: list[Intersection] = []
    c_constant = point_a[1] - m_grad * point_a[0]

    # Check intersection with each side of the bounding box
    # Left side (x = xmin)
    y = m_grad * bounding_box.xmin + c_constant
    if bounding_box.ymin <= y <= bounding_box.ymax:
        intersections.append(
            Intersection(coordinates=(bounding_box.xmin, y), edge=Edges.left)
        )

    # Right side (x = xmax)
    y = m_grad * bounding_box.xmax + c_constant
    if bounding_box.ymin <= y <= bounding_box.ymax:
        intersections.append(
            Intersection(coordinates=(bounding_box.xmax, y), edge=Edges.right)
        )

    # Bottom side (y = ymin)
    x = (bounding_box.ymin - c_constant) / m_grad
    if bounding_box.xmin <= x <= bounding_box.xmax:
        intersections.append(
            Intersection(coordinates=(x, bounding_box.ymin), edge=Edges.bottom)
        )

    # Top side (y = ymax)
    x = (bounding_box.ymax - c_constant) / m_grad
    if bounding_box.xmin <= x <= bounding_box.xmax:
        intersections.append(
            Intersection(coordinates=(x, bounding_box.ymax), edge=Edges.top)
        )

    main_intersection: Intersection = None
    for intersection in intersections:
        if check_point_is_within(
            point_a=point_a, point_b=point_b, point_c=intersection.coordinates
        ):
            main_intersection = intersection
    if main_intersection is None:
        raise IntersectionException(
            f"No intersections found for these coordinates ({coordinates}) in this bounding box ({bounding_box}). \
                Consider enlarging the bounding box or checking that your points are where you expect them to be."
        )

    return main_intersection


def get_bounding_segments(
    bounding_box: BoundingBox, bounding_box_intersections: dict[str, list]
):
    bounding_segments = []
    for k, list_of_intersections in bounding_box_intersections.items():
        if k in [Edges.top.value, Edges.bottom.value]:
            y_val = bounding_box.ymax if k == Edges.top.value else bounding_box.ymin
            start_point = (
                bounding_box.xmin,
                y_val,
            )
            end_point = (
                bounding_box.xmax,
                y_val,
            )

            list_of_intersections = sorted(list_of_intersections)
            list_of_intersections.insert(0, start_point)
            list_of_intersections.append(end_point)
        else:
            x_val = bounding_box.xmax if k == Edges.right.value else bounding_box.xmin
            start_point = (
                x_val,
                bounding_box.ymin,
            )
            end_point = (
                x_val,
                bounding_box.ymax,
            )
            list_of_intersections.sort(key=lambda x: x[1])
            list_of_intersections.insert(0, start_point)
            list_of_intersections.append(end_point)

        bounding_segments.extend(
            [
                (list_of_intersections[i], list_of_intersections[i + 1])
                for i in range(len(list_of_intersections) - 1)
            ]
        )
    return bounding_segments


def match_point_features_to_polygons(
    polygons: list[Polygon], features: list
) -> tuple[Polygon, dict]:
    polygon_point_pairs = []
    for feature in features:
        for polygon in polygons:
            if not polygon.contains(shape(feature["geometry"])):
                continue
            polygon_point_pairs.append((polygon, feature))
            break
    return polygon_point_pairs
