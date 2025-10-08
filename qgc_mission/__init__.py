# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@lechnology.com>

import json
from dataclasses import dataclass, field
from typing import Any, Sequence

from qgc_mission.enums import (
    AltitudeMode,
    Command,
    FirmwareType,
    Frame,
    VehicleType,
)


__all__ = [
    "PlanFile",
    "Mission",
    "SimpleItem",
    "GeoFence",
    "RallyPoints",
    "ComplexItem",
    "CircleGeoFence",
    "PolygonGeoFence",
]


@dataclass
class SimpleItem:
    do_jump_id: int
    """The target id for the current mission item in DO_JUMP commands. These are auto-numbered from 1."""
    command: Command
    """The scheduled action for the waypoint."""
    altitude: float
    frame: Frame
    """The coordinate system of the waypoint."""
    params: tuple[
        float | None,
        float | None,
        float | None,
        float | None,
        float | None,
        float | None,
        float | None,
    ]
    altitude_mode: AltitudeMode = AltitudeMode.MIXED
    auto_continue: bool = True
    """Auto-continue to next waypoint. Set false to pause mission after the
    item completes."""
    amsl_alt_above_terrain: float | None = None
    """Altitude value shown to the user."""


@dataclass
class ComplexItem:
    pass


@dataclass
class Mission:
    firmware_type: FirmwareType
    """The firmware type for which this mission was created."""
    vehicle_type: VehicleType
    """The vehicle type for which this mission was created."""
    global_plan_altitude_mode: AltitudeMode
    """The global plan-wide altitude mode setting. This is used by plan items
    that don't specify an "AltitudeMode"."""
    planned_home_position: tuple[float, float, float]
    """The planned home position is shown on the map and used for mission
    planning when no vehicle is connected. A tuple containing: latitude,
    longitude and AMSL altitude."""
    cruise_speed: int
    """The default forward speed for Fixed wing or VTOL vehicles (i.e. when
    moving between waypoints)."""
    hover_speed: int
    """The default forward speed for multi-rotor vehicles."""
    items: Sequence[SimpleItem | ComplexItem]
    """The list of mission item objects associated with the mission."""


@dataclass
class CircleGeoFence:
    center: tuple[float, float]
    """The center of the circle in (latitude, longitude) format."""
    radius: float
    """The radius of the circle in meters."""
    enabled: bool = True
    """Whether the geofence is enabled or not."""


@dataclass
class PolygonGeoFence:
    points: list[tuple[float, float]]
    """A list of points that define the polygon in (latitude, longitude) format.
    The points are ordered in a clockwise winding."""
    enabled: bool = True
    """Whether the geofence is enabled or not."""


@dataclass
class GeoFence:
    circles: list[CircleGeoFence] = field(default_factory=list)
    polygons: list[CircleGeoFence] = field(default_factory=list)


@dataclass
class RallyPoints:
    points: list[tuple[float, float, float]] = field(default_factory=list)


@dataclass
class PlanFile:
    ground_station: str
    """The name of the ground station which created this."""

    mission: Mission
    """The mission associated with this flight plan."""

    geo_fence: GeoFence = field(default_factory=GeoFence)
    """Geofence information for this plan."""

    rally_points: RallyPoints = field(default_factory=RallyPoints)
    """Rally/Safe point information for this plan."""


class QgcJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        match o:
            case CircleGeoFence():
                return {
                    "circle": {
                        "center": o.center,
                        "radius": o.radius,
                    },
                    "inclusion": o.enabled,
                    "version": 1,
                }
            case PolygonGeoFence():
                return {
                    "inclusion": o.enabled,
                    "polygon": o.points,
                    "version": 1,
                }
            case GeoFence():
                return {
                    "circles": o.circles,
                    "polygons": o.polygons,
                    "version": 2,
                }
            case RallyPoints():
                return {
                    "points": o.points,
                    "version": 2,
                }
            case SimpleItem():
                return {
                    "AMSLAltAboveTerrain": o.amsl_alt_above_terrain,
                    "Altitude": o.altitude,
                    "AltitudeMode": o.altitude_mode,
                    "autoContinue": o.auto_continue,
                    "command": o.command,
                    "doJumpId": o.do_jump_id,
                    "frame": o.frame,
                    "params": o.params,
                    "type": "SimpleItem",
                }
            case Mission():
                return {
                    "cruiseSpeed": o.cruise_speed,
                    "firmwareType": o.firmware_type,
                    "globalPlanAltitudeMode": o.global_plan_altitude_mode,
                    "hoverSpeed": o.hover_speed,
                    "items": o.items,
                    "plannedHomePosition": o.planned_home_position,
                    "vehicleType": o.vehicle_type,
                    "version": 2,
                }
            case PlanFile():
                return {
                    "fileType": "Plan",
                    "geoFence": o.geo_fence,
                    "groundStation": o.ground_station,
                    "mission": o.mission,
                    "rallyPoints": o.rally_points,
                    "version": 1,
                }
            case _:
                return super().default(o)
