from typing import NamedTuple


__all__ = [
    "NavTakeoffParams",
]


# https://mavlink.io/en/messages/common.html#MAV_CMD_NAV_WAYPOINT
class NavWaypointParams(NamedTuple):
    hold: float = 0
    """Hold time. (ignored by fixed wing, time to stay at waypoint for rotary
    wing) (seconds)"""
    accept_radius: float = 0
    """Acceptance radius (if the sphere with this radius is hit, the waypoint
    counts as reached) (meters)"""
    pass_radius: float = 0
    """0 to pass through the WP, if > 0 radius to pass by WP. Positive value
    for clockwise orbit, negative value for counter-clockwise orbit. Allows
    trajectory control. (meters)"""
    yaw: float | None = None
    """Desired yaw angle at waypoint (rotary wing). ``None`` to use the current
    system yaw heading mode (e.g. yaw towards next waypoint, yaw to home, etc.)
    (degrees)"""
    latitude: float = 0
    """Latitude"""
    longitude: float = 0
    """Longitude"""
    altitude: float = 0
    """Altitude (meters)"""


# https://mavlink.io/en/messages/common.html#MAV_CMD_NAV_RETURN_TO_LAUNCH
class ReturnToLaunchParams(NamedTuple):
    param1: float = 0
    param2: float = 0
    param3: float = 0
    param4: float = 0
    param5: float = 0
    param6: float = 0
    param7: float = 0


# https://mavlink.io/en/messages/common.html#MAV_CMD_NAV_TAKEOFF
class NavTakeoffParams(NamedTuple):
    """
    Parameters for the NAV_TAKEOFF command.
    """

    pitch: float = 0
    """	Minimum pitch (if airspeed sensor present), desired pitch without sensor. (degrees)"""
    param2: float = 0
    param3: float = 0
    yaw: float | None = None
    """Yaw angle (if magnetometer present), ignored without magnetometer.
    ``None`` to use the current system yaw heading mode (e.g. yaw towards next
    waypoint, yaw to home, etc.)."""
    latitude: float = 0
    longitude: float = 0
    altitude: float = 0
