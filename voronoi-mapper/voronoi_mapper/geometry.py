import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon, shape
from voronoi_mapper.models import (
    BoundingBox,
    Edges,
    Intersection,
    IntersectionException,
)


def calculate_gradient(point_a: list[float], point_b: list[float]) -> float | None:
    """Calculate the gradient of the line segment between point A and point B."""
    try:
        return (point_b[1] - point_a[1]) / (point_b[0] - point_a[0])
    except ZeroDivisionError:
        # vertical line
        return None


def check_point_is_within(
    point_a: list[float], point_b: list[float], point_c: list[float]
):
    """Checks if point_b is between point_a and point_c.

    Assumes they are colinear.
    """
    return (
        min(point_a[0], point_c[0]) <= point_b[0] <= max(point_a[0], point_c[0])
    ) and (min(point_a[1], point_c[1]) <= point_b[1] <= max(point_a[1], point_c[1]))


def handle_straight_lines(
    point_a: list[float],
    point_b: list[float],
    gradient: float | None,
    bounding_box: BoundingBox,
):
    if gradient == 0:
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


def calculate_slanted_intersections(
    point_a: list[float], gradient: float, bounding_box: BoundingBox
) -> list[Intersection]:
    intersections: list[Intersection] = []
    c_constant = point_a[1] - gradient * point_a[0]

    # check intersection with each side of the bounding box
    # left side (x = xmin)
    y = gradient * bounding_box.xmin + c_constant
    if bounding_box.ymin <= y <= bounding_box.ymax:
        intersections.append(
            Intersection(coordinates=(bounding_box.xmin, y), edge=Edges.left)
        )

    # right side (x = xmax)
    y = gradient * bounding_box.xmax + c_constant
    if bounding_box.ymin <= y <= bounding_box.ymax:
        intersections.append(
            Intersection(coordinates=(bounding_box.xmax, y), edge=Edges.right)
        )

    # bottom side (y = ymin)
    x = (bounding_box.ymin - c_constant) / gradient
    if bounding_box.xmin <= x <= bounding_box.xmax:
        intersections.append(
            Intersection(coordinates=(x, bounding_box.ymin), edge=Edges.bottom)
        )

    # top side (y = ymax)
    x = (bounding_box.ymax - c_constant) / gradient
    if bounding_box.xmin <= x <= bounding_box.xmax:
        intersections.append(
            Intersection(coordinates=(x, bounding_box.ymax), edge=Edges.top)
        )
    return intersections


def find_main_intersection(
    point_a, point_b, intersections: list[Intersection]
) -> Intersection | None:
    main_intersection: Intersection | None = None
    for intersection in intersections:
        if check_point_is_within(
            point_a=point_a, point_b=point_b, point_c=intersection.coordinates
        ):
            main_intersection = intersection
    return main_intersection


def get_intersection_with_bounding_box(
    coordinates: tuple[list[float], list[float]], bounding_box: BoundingBox
) -> Intersection:
    """
    Calculate the intersection of a line segment defined by two points with a bounding box.

    Parameters:
    - coordinates (Tuple[List[float], List[float]]): A tuple containing two lists representing point A and point B.
    - bounding_box (BoundingBox): An instance of BoundingBox defining the area of interest.

    Returns:
    - Intersection: An instance of Intersection containing the coordinates of the intersection and the edge it intersects with.

    Raises:
    - IntersectionException: If no intersection is found within the bounding box.
    """
    point_a, point_b = coordinates
    gradient = calculate_gradient(point_a, point_b)

    # handle horizontal and vertical lines
    if gradient in [0, None]:
        return handle_straight_lines(point_a, point_b, gradient, bounding_box)

    intersections = calculate_slanted_intersections(point_a, gradient, bounding_box)
    main_intersection = find_main_intersection(point_a, point_b, intersections)

    if main_intersection is None:
        raise IntersectionException(
            f"No intersections found for coordinates {coordinates} in this bounding box {bounding_box}."
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


def clip_polygons_to_mask(
    gdf: gpd.GeoDataFrame, mask: MultiPolygon
) -> gpd.GeoDataFrame:
    return gdf.clip(mask=mask)
