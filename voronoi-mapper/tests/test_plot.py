import os

import pytest
from shapely.geometry import MultiPolygon, Polygon
from voronoi_mapper.plot import plot_voronoi


@pytest.mark.parametrize(
    "mask",
    [
        (Polygon([(1, 1), (3, 1), (3, 3), (1, 3)])),
        (MultiPolygon([Polygon([(1, 1), (3, 1), (3, 3), (1, 3)])])),
    ],
)
def test_plot_voronoi(mock_voronoi, mock_bounding_box, mask, temp_directory):
    file_name = "test_image.png"
    file_path = os.path.join(temp_directory, file_name)
    plot_voronoi(
        voronoi=mock_voronoi,
        save_path=file_path,
        boundary=mask,
        bounding_box=mock_bounding_box,
    )

    assert file_name in os.listdir(temp_directory)
