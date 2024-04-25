import json
import os
from pdb import set_trace

from voronoi_mapper.voronoi import voronoi_map


def test_voronoi_map(
    mock_saved_geojson_file_path, mock_saved_geojson_mask_file_path, temp_directory
):
    FILE_NAME = "saved_file.geojson"
    GEOJSON_SAVE_PATH = os.path.join(temp_directory, FILE_NAME)

    voronoi_map(
        features_file_path=mock_saved_geojson_file_path,
        boundary_file_path=mock_saved_geojson_mask_file_path,
        save_path=GEOJSON_SAVE_PATH,
    )

    assert FILE_NAME in os.listdir(temp_directory)
