import math
from skywrangler_web_server.geo import (
    latlon_to_utm,
    origin_alt_to_takeoff_alt,
    utm_to_latlon,
    dist_ang_to_horiz_vert,
)


def test_conversion():
    x, y, t = latlon_to_utm(37.4137157, -121.9961280)
    assert math.isclose(x, 588835.5227042, rel_tol=1e-7)
    assert math.isclose(y, 4141241.6621166, rel_tol=1e-7)

    lat, lon = utm_to_latlon(x, y, t)
    assert math.isclose(lat, 37.4137157, rel_tol=1e-7)
    assert math.isclose(lon, -121.9961280, rel_tol=1e-7)


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
