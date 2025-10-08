from itertools import count
from qgc_mission import Mission, PlanFile, SimpleItem
from qgc_mission.enums import AltitudeMode, Command, FirmwareType, Frame, VehicleType
from qgc_mission.params import NavTakeoffParams, NavWaypointParams, ReturnToLaunchParams
from sw_mission.geo import (
    diagonal_point,
    dist_ang_to_horiz_vert,
    origin_alt_to_takeoff_alt,
)
from sw_mission.points import (
    Coordinate2D,
    Point,
    Parameters,
    Transect,
    transect_points,
)


SAFE_ALTITUDE = 100  # meters
SPEED = 10  # meters per second


def create_mission(
    launch: Point,
    origin: Point,
    transect: Transect,
    parameters: Parameters,
    return_point: Coordinate2D,
) -> PlanFile:
    jump_id = count(1)

    _horizontal, vertical = dist_ang_to_horiz_vert(
        parameters.distance, parameters.angle
    )
    c, d = transect_points(origin, transect, parameters)

    # mission items need altitudes relative to takeoff altitude
    relative_vertical = origin_alt_to_takeoff_alt(
        vertical, origin.altitude, launch.altitude
    )
    b_lat, b_long = diagonal_point(
        c.latitude,
        c.longitude,
        SAFE_ALTITUDE - relative_vertical,
        transect.azimuth - 90,
    )
    e_lat, e_long = diagonal_point(
        d.latitude,
        d.longitude,
        SAFE_ALTITUDE - relative_vertical,
        transect.azimuth + 90,
    )
    f_lat, f_long = return_point.latitude, return_point.longitude

    mission_items: list[SimpleItem] = []

    # Point A is taking off to safe altitude above launch
    mission_items.append(
        SimpleItem(
            do_jump_id=next(jump_id),
            command=Command.NAV_TAKEOFF,
            altitude_mode=AltitudeMode.LAUNCH,
            altitude=SAFE_ALTITUDE,
            frame=Frame.GLOBAL_RELATIVE_ALT,
            params=NavTakeoffParams(
                latitude=launch.latitude,
                longitude=launch.longitude,
                altitude=SAFE_ALTITUDE,
            ),
        )
    )

    # Flies to line colinear of the transect
    # Point B
    mission_items.append(
        SimpleItem(
            do_jump_id=next(jump_id),
            command=Command.NAV_WAYPOINT,
            altitude_mode=AltitudeMode.AMSL,
            altitude=launch.altitude + SAFE_ALTITUDE,
            frame=Frame.GLOBAL,
            params=NavWaypointParams(
                latitude=b_lat,
                longitude=b_long,
                altitude=launch.altitude + SAFE_ALTITUDE,
            ),
        )
    )
    # flies at an angle of 60 degrees towards the start of the transect
    # Point C
    mission_items.append(
        SimpleItem(
            do_jump_id=next(jump_id),
            command=Command.NAV_WAYPOINT,
            altitude_mode=AltitudeMode.AMSL,
            altitude=launch.altitude + SAFE_ALTITUDE,
            frame=Frame.GLOBAL,
            params=NavWaypointParams(
                latitude=c.latitude,
                longitude=c.longitude,
                altitude=c.altitude,
            ),
        )
    )
    # Flies at requested speed and requested altitude to the end of the transect
    # Point D
    mission_items.append(
        SimpleItem(
            do_jump_id=next(jump_id),
            command=Command.NAV_WAYPOINT,
            altitude_mode=AltitudeMode.AMSL,
            altitude=launch.altitude + SAFE_ALTITUDE,
            frame=Frame.GLOBAL,
            params=NavWaypointParams(
                latitude=d.latitude,
                longitude=d.longitude,
                altitude=d.altitude,
            ),
        )
    )
    # ascends at 60 degrees towards the safe altitude towards the return point
    # Point E
    mission_items.append(
        SimpleItem(
            do_jump_id=next(jump_id),
            command=Command.NAV_WAYPOINT,
            altitude_mode=AltitudeMode.AMSL,
            altitude=launch.altitude + SAFE_ALTITUDE,
            frame=Frame.GLOBAL,
            params=NavWaypointParams(
                latitude=e_lat,
                longitude=e_long,
                altitude=launch.altitude + SAFE_ALTITUDE,
            ),
        )
    )
    # Flies at a safe altitude and returns to launch
    # Point F
    mission_items.append(
        SimpleItem(
            do_jump_id=next(jump_id),
            command=Command.NAV_WAYPOINT,
            altitude_mode=AltitudeMode.AMSL,
            altitude=launch.altitude + SAFE_ALTITUDE,
            frame=Frame.GLOBAL,
            params=NavWaypointParams(
                latitude=f_lat,
                longitude=f_long,
                altitude=launch.altitude + SAFE_ALTITUDE,
            ),
        )
    )

    mission_items.append(
        SimpleItem(
            do_jump_id=next(jump_id),
            command=Command.NAV_RETURN_TO_LAUNCH,
            altitude_mode=AltitudeMode.LAUNCH,
            altitude=SAFE_ALTITUDE,
            frame=Frame.MISSION,
            params=ReturnToLaunchParams(),
        )
    )

    plan = PlanFile(
        ground_station="SkyWrangler",
        mission=Mission(
            firmware_type=FirmwareType.PX4,
            vehicle_type=VehicleType.QUADROTOR,
            global_plan_altitude_mode=AltitudeMode.MIXED,
            hover_speed=SPEED,
            cruise_speed=SPEED,
            planned_home_position=launch,
            items=mission_items,
        ),
    )

    return plan
