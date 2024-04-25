from voronoi_mapper.voronoi import voronoi_map

if __name__ == "__main__":
    POINTS_GEOJSON_PATH = "./_data/points.geojson"
    BOUNDARY_GEOJSON_PATH = "./_data/wales.geojson"
    GEOJSON_SAVE_PATH = "./_data/wales_parkrun_polygons.geojson"

    voronoi_map(
        features_file_path=POINTS_GEOJSON_PATH,
        boundary_file_path=BOUNDARY_GEOJSON_PATH,
        save_path=GEOJSON_SAVE_PATH,
    )
