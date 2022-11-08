from typing import NamedTuple, Tuple

from .geo import dist_ang_to_horiz_vert, relative_point


class Point(NamedTuple):

    latitude: float
    longitude: float
    altitue: float


class Origin(NamedTuple):
    """
    The origin point - i.e. the center of the enclosure.
    """

    latitude: float
    longitude: float
    elevation: float


class Transect(NamedTuple):
    """
    The transect line.
    """

    azimuth: float
    length: float


class Parameters(NamedTuple):
    """
    The experiment parameters (variables).
    """

    speed: float
    distance: float
    angle: float


def transect_points(
    origin: Origin, transect: Transect, parameters: Parameters
) -> Tuple[Point, Point]:

    horizontal, vertical = dist_ang_to_horiz_vert(parameters.distance, parameters.angle)
    m_lat, m_lon = relative_point(
        origin.latitude, origin.longitude, horizontal, transect.azimuth
    )
    b_lat, b_lon = relative_point(
        m_lat, m_lon, transect.length / 2, transect.azimuth - 90
    )
    c_lat, c_lon = relative_point(
        m_lat, m_lon, transect.length / 2, transect.azimuth + 90
    )
    return (
        Point(b_lat, b_lon, origin.elevation + vertical),
        Point(c_lat, c_lon, origin.elevation + vertical),
    )
