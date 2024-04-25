from scipy.spatial import Voronoi
from voronoi_mapper.geojson import (
    load_mask_geojson,
    load_points_and_features_from_geojson,
)
from voronoi_mapper.models import BoundingBox
from voronoi_mapper.plot import plot_voronoi

if __name__ == "__main__":
    POINTS_GEOJSON_PATH = "./_data/points.geojson"
    BOUNDARY_GEOJSON_PATH = "./_data/wales.geojson"

    points, _ = load_points_and_features_from_geojson(geojson_path=POINTS_GEOJSON_PATH)
    mask = load_mask_geojson(geojson_path=BOUNDARY_GEOJSON_PATH)

    bounding_box = BoundingBox(xmin=-6, xmax=-1, ymin=51, ymax=54)

    voronoi = Voronoi(points)

    plot_voronoi(
        voronoi=voronoi,
        bounding_box=bounding_box,
        boundary=mask,
        save_path="./_data/_plots/voronoi.png",
    )
