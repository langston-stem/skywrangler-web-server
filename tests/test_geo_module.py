from skywrangler_web_server.geo import latlon_to_utm, utm_to_latlon


def test_conversion():
    x, y, t = latlon_to_utm(37.4137157, -121.9961280)
    assert x, y == (588835.5182558, 4141241.6642884)

    lat, lon = utm_to_latlon(x, y, t)
    assert lat, lon == (37.4137157, -121.9961280)