_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.0">
"""

_FOOTER = """
</kml>
"""

_DEFAULT_PLACEMARK = """
            <Placemark>
                <name>"{}"</name>
                <Point>
                    <coordinates>{},{},0</coordinates>
                </Point>
            </Placemark>
            """


def dict_to_kml(data: dict) -> str:
    """
    Converts a dictionary of the format

    Args:
        data:

    Returns:

    """
    kml = _HEADER
    for (lon, lat), value in data.items():
        kml += _DEFAULT_PLACEMARK.format(value, lat, lon)
    return kml + _FOOTER
