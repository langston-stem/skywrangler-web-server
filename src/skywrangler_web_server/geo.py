"""
Geo reference helper functions.
"""

from math import sin, cos, tan, pi
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

    return *transformer.transform(latitude, longitude), Transformer.from_crs(
        crs, crs.geodetic_crs
    )


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
    return transformer.transform(x, y)


def relative_point(
    latitude: float, longitude: float, distance: float, azimuth: float
) -> Tuple[float, float]:
    """
    converts reference latitude and longitude to start_x and start_y, then start_x and start_y to meters

    combines start_x and start_y with delta_X and delta_Y to create new (X, Y)

    then converts the new (X, Y) meters back to longitude to latitude
    """
    # This converts clockwise azimuth from north to a counter-clockwise angle from horizontal.
    angle = -azimuth + 90
    start_x, start_y, t = latlon_to_utm(latitude, longitude)
    delta_x, delta_y = dist_ang_to_horiz_vert(distance, angle)
    new_x = start_x + delta_x
    new_y = start_y + delta_y
    return utm_to_latlon(new_x, new_y, t)


def diagonal_point(
    latitude: float, longitude: float, height: float, azimuth: float
) -> Tuple[float, float]:
    """
    converts reference latitude and longitude to a new longitude and latitude based on

    the height and azimuth parameter at a fixed angle of 60 degrees.
    """
    # This converts clockwise azimuth from north to a counter-clockwise angle from horizontal.
    angle = -azimuth + 90
    start_x, start_y, t = latlon_to_utm(latitude, longitude)
    horizontal = angle_and_height_to_distance(60, height)
    delta_x, delta_y = dist_ang_to_horiz_vert(horizontal, angle)
    new_x = start_x + delta_x
    new_y = start_y + delta_y

    return utm_to_latlon(new_x, new_y, t)


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


def angle_and_height_to_distance(angle: float, height: float) -> float:
    """converts the angle and relative altitude to a distance in between B and C.
    angle: The angle in degrees.
    """
    horizontal = height / tan(angle * pi / 180)
    return horizontal
