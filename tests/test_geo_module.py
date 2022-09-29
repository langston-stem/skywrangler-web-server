import math
from skywrangler_web_server.geo import (
    latlon_to_utm,
    origin_alt_to_takeoff_alt,
    utm_to_latlon,
    dist_ang_to_horiz_vert,
)


def test_conversion():
    x, y, t = latlon_to_utm(37.4137157, -121.9961280)
    assert x, y == (588835.5182558, 4141241.6642884)

    lat, lon = utm_to_latlon(x, y, t)
    assert lat, lon == (37.4137157, -121.9961280)


def test_alt_conversion():
    alt = origin_alt_to_takeoff_alt(5, 998, 1000)
    assert alt == 3


def test_dist_ang_to_horiz_vert():
    horizontal, vertical = dist_ang_to_horiz_vert(30, 90)
    assert math.isclose(horizontal, 0.0, abs_tol=0.05)
    assert math.isclose(vertical, 30.0, abs_tol=0.05)

    horizontal, vertical = dist_ang_to_horiz_vert(15, 60)
    assert math.isclose(horizontal, 7.5, abs_tol=0.05)
    assert math.isclose(vertical, 13.0, abs_tol=0.05)

    horizontal, vertical = dist_ang_to_horiz_vert(3, 30)
    assert math.isclose(horizontal, 2.6, abs_tol=0.05)
    assert math.isclose(vertical, 1.5, abs_tol=0.05)
