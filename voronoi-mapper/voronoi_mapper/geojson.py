import json


def _load_geojson_file(geojson_path: str):
    # TODO: extend to yaml
    with open(geojson_path, "r", encoding="utf-8") as f:
        points_geojson_obj = json.load(f)
    return points_geojson_obj


def load_points_and_features_from_geojson(
    geojson_path: str,
) -> tuple[list[list[float]], list[dict[str, str]]]:
    geojson_obj = _load_geojson_file(geojson_path=geojson_path)

    features = geojson_obj["features"]
    geom = [shape(i["geometry"]) for i in features]
    points = [shp.get_coordinates(x).tolist() for x in geom]
    points = [item[0] for item in points]

    return points, features


def load_mask_geojson(geojson_path: str):
    boundary_geojson_obj = _load_geojson_file(geojson_path=geojson_path)

    geometries = [shape(x["geometry"]) for x in boundary_geojson_obj["features"]]

    unified_shape = unary_union(geoms=geometries)
    return unified_shape
