_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <Document>
        <name>CLimate Data</name>
        <atom:author>
            <atom:name>U.S. Geological Survey</atom:name>
        </atom:author>
        <atom:link href="http://earthquake.usgs.gov"/>
        <Folder>"""

_FOOTER = """
        </Folder>
    </Document>
</kml>
"""

_DEFAULT_PLACEMARK = """
            <Placemark id="{} {} {} ">
                <name>"M {} {}"</name>
                <magnitude>{}</magnitude>
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
        kml += _DEFAULT_PLACEMARK.format("Some ID", lat, lon, value, "Some Name", value, lat, lon)
    return kml + _FOOTER
