import math
from skywrangler_web_server.mission import (
    Origin,
    Parameters,
    Point,
    Transect,
    transect_points,
)


def point_is_close(a: Point, b: Point):
    assert math.isclose(a.latitude, b.latitude, rel_tol=1e-7)
    assert math.isclose(a.longitude, b.longitude, rel_tol=1e-7)
    assert math.isclose(a.altitue, b.altitue, rel_tol=1e-7)


def test_transect_points():
    origin = Origin(35.9459702, -97.2586730, 77.7)
    transect = Transect(0, 40)
    parameters = Parameters(5, 30, 90)

    point_b, point_c = transect_points(origin, transect, parameters)

    point_is_close(point_b, Point(35.9459734, -97.2588947, 107.7))
    point_is_close(point_c, Point(35.9459670, -97.2584513, 107.7))

    origin = Origin(35.9459702, -97.2586730, 77.7)
    transect = Transect(45, 40)
    parameters = Parameters(2, 7, 30)

    point_b, point_c = transect_points(origin, transect, parameters)

    point_is_close(point_b, Point(35.9461381, -97.2587783, 81.2))
    point_is_close(point_c, Point(35.9458787, -97.2584704, 81.2))
