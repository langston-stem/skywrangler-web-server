import json
from itertools import count
from typing import cast
from qgc_mission import (
    GeoFence,
    Mission,
    PlanFile,
    PolygonGeoFence,
    RallyPoints,
    SimpleItem,
    CircleGeoFence,
    QgcJSONEncoder,
)
from qgc_mission.enums import AltitudeMode, Command, Frame, VehicleType, FirmwareType
from qgc_mission.params import NavTakeoffParams


def test_mission():
    next_id = count(1)

    mission = Mission(
        firmware_type=FirmwareType.PX4,
        vehicle_type=VehicleType.QUADROTOR,
        global_plan_altitude_mode=AltitudeMode.LAUNCH,
        hover_speed=5,
        cruise_speed=15,
        planned_home_position=(47.3977419, 8.545594, 487.989),
        items=[
            SimpleItem(
                do_jump_id=next(next_id),
                amsl_alt_above_terrain=None,
                command=Command.NAV_TAKEOFF,
                frame=Frame.GLOBAL_RELATIVE_ALT,
                params=NavTakeoffParams(
                    pitch=15, latitude=47.3985099, longitude=8.5451002, altitude=50
                ),
                altitude=50,
            )
        ],
    )
    expected_json = json.dumps(
        {
            "cruiseSpeed": 15,
            "firmwareType": 12,
            "globalPlanAltitudeMode": 1,
            "hoverSpeed": 5,
            "items": [
                {
                    "AMSLAltAboveTerrain": None,
                    "Altitude": 50,
                    "AltitudeMode": 0,
                    "autoContinue": True,
                    "command": 22,
                    "doJumpId": 1,
                    "frame": 3,
                    "params": [15, 0, 0, None, 47.3985099, 8.5451002, 50],
                    "type": "SimpleItem",
                }
            ],
            "plannedHomePosition": [47.3977419, 8.545594, 487.989],
            "vehicleType": 2,
            "version": 2,
        },
        indent=2,
    )

    assert json.dumps(mission, cls=QgcJSONEncoder, indent=2) == expected_json


def test_plan_file():
    # HACK: empty mission to make test simpler
    plan = PlanFile(ground_station="QGroundControl", mission=cast(Mission, {}))

    expected_json = json.dumps(
        {
            "fileType": "Plan",
            "geoFence": {
                "circles": [],
                "polygons": [],
                "version": 2,
            },
            "groundStation": "QGroundControl",
            "mission": {},
            "rallyPoints": {
                "points": [],
                "version": 2,
            },
            "version": 1,
        },
        indent=2,
    )

    assert json.dumps(plan, cls=QgcJSONEncoder, indent=2) == expected_json


def test_geofence():
    fence = GeoFence()

    expected_json = json.dumps(
        {
            "circles": [],
            "polygons": [],
            "version": 2,
        },
        indent=2,
    )
    assert json.dumps(fence, cls=QgcJSONEncoder, indent=2) == expected_json


def test_circle_geofence():
    fence = CircleGeoFence(center=(47.39756763610029, 8.544649762407738), radius=319.85)

    expected_json = json.dumps(
        {
            "circle": {
                "center": [47.39756763610029, 8.544649762407738],
                "radius": 319.85,
            },
            "inclusion": True,
            "version": 1,
        },
        indent=2,
    )

    assert json.dumps(fence, cls=QgcJSONEncoder, indent=2) == expected_json


def test_polygon_geofence():
    fence = PolygonGeoFence(
        points=[
            (47.39807773798406, 8.543834631785785),
            (47.39983519888905, 8.550024648373267),
            (47.39641100087146, 8.54499282423751),
            (47.395590322265186, 8.539435808992085),
        ]
    )
    expected_json = json.dumps(
        {
            "inclusion": True,
            "polygon": [
                [47.39807773798406, 8.543834631785785],
                [47.39983519888905, 8.550024648373267],
                [47.39641100087146, 8.54499282423751],
                [47.395590322265186, 8.539435808992085],
            ],
            "version": 1,
        },
        indent=2,
    )
    assert json.dumps(fence, cls=QgcJSONEncoder, indent=2) == expected_json


def test_rally_points():
    rally = RallyPoints(
        points=[(47.39760401, 8.5509154, 50), (47.39902017, 8.54263274, 50)]
    )

    expected_json = json.dumps(
        {
            "points": [[47.39760401, 8.5509154, 50], [47.39902017, 8.54263274, 50]],
            "version": 2,
        },
        indent=2,
    )

    assert json.dumps(rally, cls=QgcJSONEncoder, indent=2) == expected_json
