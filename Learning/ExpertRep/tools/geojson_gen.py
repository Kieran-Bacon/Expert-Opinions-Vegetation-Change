_HEADER = """{"type":"FeatureCollection","features":["""

_FOOTER = """]}"""

_DEFAULT_PLACEMARK = """{{"type": "Feature","properties": {{"weight": {}}},"geometry": {{"type": "Point","coordinates": [{},{}]}}}},"""

def dict_to_geojson(data: dict) -> str:
    geojson = _HEADER
    for (lon, lat), value in data.items():
        geojson += _DEFAULT_PLACEMARK.format(value, lat, lon)
    geojson = geojson[:-1]
    return geojson + _FOOTER