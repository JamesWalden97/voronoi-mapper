import json

import numpy as np
import pytest
from scipy.spatial import Voronoi
from shapely import from_geojson
from voronoi_mapper.models import BoundingBox


@pytest.fixture
def mock_points():
    return [[0, 0], [1, 1], [2, 3], [1, 2]]


@pytest.fixture
def mock_points_as_features(mock_points):
    return [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {"type": "Point", "coordinates": point},
        }
        for point in mock_points
    ]


@pytest.fixture
def mock_voronoi(mock_points):
    points = np.array(mock_points)
    return Voronoi(points)


@pytest.fixture
def mock_bounding_box():
    return BoundingBox(xmin=-10, xmax=10, ymin=-10, ymax=10)


@pytest.fixture
def mock_bounding_box_intersections():
    return {
        "top": [[-6.0, 10]],
        "right": [[10, -2.25], [10, -9.0]],
        "bottom": [],
        "left": [[-10, 6.25]],
    }


@pytest.fixture
def mock_expected_polygons():
    _polygons = [
        {
            "type": "Polygon",
            "coordinates": [
                [[-0.5, 1.5], [2.5, 1.5], [10.0, -2.25], [10.0, -9.0], [-0.5, 1.5]]
            ],
        },
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [2.5, 1.5],
                    [-0.5, 1.5],
                    [-10.0, 6.25],
                    [-10.0, 10.0],
                    [-6.0, 10.0],
                    [2.5, 1.5],
                ]
            ],
        },
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [-0.5, 1.5],
                    [10.0, -9.0],
                    [10.0, -10.0],
                    [-10.0, -10.0],
                    [-10.0, 6.25],
                    [-0.5, 1.5],
                ]
            ],
        },
        {
            "type": "Polygon",
            "coordinates": [
                [[2.5, 1.5], [-6.0, 10.0], [10.0, 10.0], [10.0, -2.25], [2.5, 1.5]]
            ],
        },
    ]

    return [from_geojson(json.dumps(_polygon)) for _polygon in _polygons]
