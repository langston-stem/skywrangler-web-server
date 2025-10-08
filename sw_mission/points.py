from typing import NamedTuple

from sw_mission.geo import dist_ang_to_horiz_vert, relative_point


class Point(NamedTuple):
    latitude: float
    longitude: float
    altitude: float


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


class Coordinate2D(NamedTuple):
    """
    2D coordinate - i.e. allows us to input a coordinate but only on a 2D scale.
    """

    latitude: float
    longitude: float


def transect_points(
    origin: Point, transect: Transect, parameters: Parameters
) -> tuple[Point, Point]:
    """
    Calculates transect start and end points based on the experiment parameters.

    Args:
        origin: The center of the goat enclosure.
        transect: The path of the drone as it passes by the enclosure.
        paramters: The variable parameters of the experiment.

    Returns:
        A tuple of the starting and ending transect points.
    """

    horizontal, vertical = dist_ang_to_horiz_vert(parameters.distance, parameters.angle)

    # m is the midpoint of the transect
    m_lat, m_lon = relative_point(
        origin.latitude, origin.longitude, horizontal, transect.azimuth
    )
    # b is the starting point of the transect
    b_lat, b_lon = relative_point(
        m_lat, m_lon, transect.length / 2, transect.azimuth - 90
    )
    # c is the ending point of the transect
    c_lat, c_lon = relative_point(
        m_lat, m_lon, transect.length / 2, transect.azimuth + 90
    )

    return (
        Point(b_lat, b_lon, origin.altitude + vertical),
        Point(c_lat, c_lon, origin.altitude + vertical),
    )
