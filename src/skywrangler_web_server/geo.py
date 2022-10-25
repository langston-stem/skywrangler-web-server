"""
Geo reference helper functions.
"""

from math import sin, cos, pi
from typing import Tuple

from pyproj import CRS, Transformer
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info


def _find_utm_crs(latitude: float, longitude: float) -> CRS:
    """
    Gets the UTM coordinate reference system for a given latitude and longitude.

    Args:
        latitude: The latitude in degrees.
        longitude: The longitude in degrees.

    Returns:
        The UTM coordinate referene system.
    """
    utm_crs_list = query_utm_crs_info(
        datum_name="WGS 84",
        area_of_interest=AreaOfInterest(
            west_lon_degree=longitude,
            south_lat_degree=latitude,
            east_lon_degree=longitude,
            north_lat_degree=latitude,
        ),
    )
    utm_crs = CRS.from_epsg(utm_crs_list[0].code)
    return utm_crs


def latlon_to_utm(
    latitude: float, longitude: float
) -> Tuple[float, float, Transformer]:
    """
    Converts latitude and longitude to UTM reference system.

    Args:
        latitude: The latitude in degrees.
        longitude: The longitude in degrees.

    Returns:
        A tuple of the x and y coordinates in meters (UTM easting an northing)
        and the transformer used for the conversion.
    """
    crs = _find_utm_crs(latitude, longitude)

    # transformer that converts from latlon to utm
    transformer = Transformer.from_crs(crs.geodetic_crs, crs)

    return *transformer.transform(latitude, longitude), transformer


def utm_to_latlon(x: float, y: float, transformer: Transformer) -> Tuple[float, float]:
    """
    Converts easting and norting from UTM reference system to latitude and longitude.

    Args:
        x: The x coordinate in meters (UTM easting).
        y: The y coordinate in meters (UTM northing).
        transformer: The transfomer that was used for the convertion to UTM.

    Returns:
        A tuple of the latitude and longitude in degrees.
    """
    return next(transformer.itransform([(x, y)]))


def origin_alt_to_takeoff_alt(
    altitude: float, origin_elevation: float, takeoff_elevation: float
) -> float:
    """
    Converts an altitude relative to the origin to an altitude relative to the takeoff position.

    Args:
        altitude: the target altitude relative to the origin in meters
        origin_elevation: the elevation of the origin in meters
        takeoff_elevation: the UAV takeoff elevation in meters

    Returns:
        The target altitude relative to the origin elevation.
    """
    rel_altitude = altitude - (takeoff_elevation - origin_elevation)
    return rel_altitude


def dist_ang_to_horiz_vert(distance: float, angle: float) -> Tuple[float, float]:
    """
    Converts a distance and angle into horizontal and vertical components.

    Args:
        distance: The distance in meters.
        angle: The angle from the horizontal in degrees.

    Returns:
        A tuple of the horizontal and vertical components in meters.
    """
    horizontal = cos(angle * pi / 180) * distance
    vertical = sin(angle * pi / 180) * distance
    return horizontal, vertical
