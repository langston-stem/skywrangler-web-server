# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@lechnology.com>

from enum import IntEnum

__all__ = [
    "Command",
    "Frame",
    "FirmwareType",
    "VehicleType",
    "AltitudeMode",
]


# https://mavlink.io/en/messages/common.html#mav_commands
class Command(IntEnum):
    """Enumeration for MAVLink command IDs."""

    NAV_WAYPOINT = 16
    """Navigate to waypoint. This is intended for use in missions."""

    NAV_LOITER_UNLIM = 17
    """Loiter around this waypoint an unlimited amount of time."""

    NAV_LOITER_TURNS = 18
    """Loiter around this waypoint for X turns."""

    NAV_LOITER_TIME = 19
    """Loiter at the specified latitude, longitude and altitude for a certain
    amount of time. Multicopter vehicles stop at the point (within a vehicle-
    specific acceptance radius). Forward-only moving vehicles (e.g. fixed-wing)
    circle the point with the specified radius/direction. If the Heading
    Required parameter (2) is non-zero forward moving aircraft will only leave
    the loiter circle once heading towards the next waypoint."""

    NAV_RETURN_TO_LAUNCH = 20
    """Return to launch location."""

    NAV_LAND = 21
    """Land at location."""

    NAV_TAKEOFF = 22
    """Takeoff from ground / hand. Vehicles that support multiple takeoff modes
    (e.g. VTOL quadplane) should take off using the currently configured mode."""

    NAV_LAND_LOCAL = 23
    """Land at local position (local frame only)."""

    NAV_TAKEOFF_LOCAL = 24
    """Takeoff from local position (local frame only)."""

    NAV_FOLLOW = 25
    """Vehicle following, i.e. this waypoint represents the position of a
    moving vehicle."""

    NAV_CONTINUE_AND_CHANGE_ALT = 30
    """Continue on the current course and climb/descend to specified altitude.
    When the altitude is reached continue to the next command (i.e., don't
    proceed to the next command until the desired altitude is reached.."""

    NAV_LOITER_TO_ALT = 31
    """Begin loiter at the specified Latitude and Longitude. If Lat=Lon=0, then
    loiter at the current position. Don't consider the navigation command
    complete (don't leave loiter) until the altitude has been reached.
    Additionally, if the Heading Required parameter is non-zero the aircraft
    will not leave the loiter until heading toward the next waypoint."""


# https://mavlink.io/en/messages/common.html#MAV_FRAME
class Frame(IntEnum):
    """Enumeration for MAVLink coordinate frames."""

    GLOBAL = 0
    """Global (WGS84) coordinate frame + altitude relative to mean sea level
    (MSL)."""

    LOCAL_NED = 1
    """NED local tangent frame (x: North, y: East, z: Down) with origin fixed
    relative to earth."""

    MISSION = 2
    """NOT a coordinate frame, indicates a mission command."""

    GLOBAL_RELATIVE_ALT = 3
    """Global (WGS84) coordinate frame + altitude relative to the home
    position."""

    LOCAL_ENU = 4
    """ENU local tangent frame (x: East, y: North, z: Up) with origin fixed
    relative to earth."""

    LOCAL_OFFSET_NED = 7
    """NED local tangent frame (x: North, y: East, z: Down) with origin that
    travels with the vehicle."""

    BODY_FRD = 12
    """FRD local frame aligned to the vehicle's attitude (x: Forward, y: Right,
    z: Down) with an origin that travels with vehicle."""

    LOCAL_FRD = 20
    """FRD local tangent frame (x: Forward, y: Right, z: Down) with origin
    fixed relative to earth. The forward axis is aligned to the front of the
    vehicle in the horizontal plane."""

    LOCAL_FLU = 21
    """FLU local tangent frame (x: Forward, y: Left, z: Up) with origin fixed
    relative to earth. The forward axis is aligned to the front of the vehicle
    in the horizontal plane."""


# https://mavlink.io/en/messages/common.html#MAV_AUTOPILOT
class FirmwareType(IntEnum):
    """Enumeration for MAV autopilot types."""

    GENERIC = 0
    """Generic autopilot, full support for everything."""

    RESERVED = 1
    """Reserved for future use."""

    SLUGS = 2
    """SLUGS autopilot, http://slugsuav.soe.ucsc.edu."""

    ARDUPILOT_MEGA = 3
    """ArduPilot - Plane/Copter/Rover/Sub/Tracker, https://ardupilot.org."""

    OPENPILOT = 4
    """OpenPilot, http://openpilot.org."""

    GENERIC_WAYPOINTS_ONLY = 5
    """Generic autopilot only supporting simple waypoints."""

    GENERIC_WAYPOINTS_AND_SIMPLE_NAVIGATION_ONLY = 6
    """Generic autopilot supporting waypoints and other simple navigation
    commands."""

    GENERIC_MISSION_FULL = 7
    """Generic autopilot supporting the full mission command set."""

    INVALID = 8
    """No valid autopilot, e.g. a GCS or other MAVLink component."""

    PPZ = 9
    """PPZ UAV - http://nongnu.org/paparazzi."""

    UDB = 10
    """UAV Dev Board."""

    FP = 11
    """FlexiPilot."""

    PX4 = 12
    """PX4 Autopilot - http://px4.io/."""

    SMACCMPILOT = 13
    """SMACCMPilot - http://smaccmpilot.org."""

    AUTOQUAD = 14
    """AutoQuad -- http://autoquad.org."""

    ARMAZILA = 15
    """Armazila -- http://armazila.com."""

    AEROB = 16
    """Aerob -- http://aerob.ru."""

    ASLUAV = 17
    """ASLUAV autopilot -- http://www.asl.ethz.ch."""

    SMARTAP = 18
    """SmartAP Autopilot - http://sky-drones.com."""

    AIRRAILS = 19
    """AirRails - http://uaventure.com."""

    REFLEX = 20
    """Fusion Reflex - https://fusion.engineering."""


# https://mavlink.io/en/messages/common.html#MAV_TYPE
class VehicleType(IntEnum):
    """Enumeration for MAV (Micro Air Vehicle) types."""

    GENERIC = 0
    """Generic micro air vehicle."""

    FIXED_WING = 1
    """Fixed wing aircraft."""

    QUADROTOR = 2
    """Quadrotor."""

    COAXIAL = 3
    """Coaxial helicopter."""

    HELICOPTER = 4
    """Normal helicopter with tail rotor."""

    ANTENNA_TRACKER = 5
    """Ground installation."""

    GCS = 6
    """Operator control unit / ground control station."""

    AIRSHIP = 7
    """Controlled airship."""

    FREE_BALLOON = 8
    """Uncontrolled free balloon."""

    ROCKET = 9
    """Rocket."""

    GROUND_ROVER = 10
    """Ground rover."""

    SURFACE_BOAT = 11
    """Surface vessel, boat, or ship."""

    SUBMARINE = 12
    """Submarine."""

    HEXAROTOR = 13
    """Hexarotor."""

    OCTOROTOR = 14
    """Octorotor."""

    TRICOPTER = 15
    """Tricopter."""

    FLAPPING_WING = 16
    """Flapping wing."""

    KITE = 17
    """Kite."""

    ONBOARD_CONTROLLER = 18
    """Onboard companion controller."""

    VTOL_TAILSITTER_DUOROTOR = 19
    """Two-rotor Tailsitter VTOL."""

    VTOL_TAILSITTER_QUADROTOR = 20
    """Quad-rotor Tailsitter VTOL."""

    VTOL_TILTROTOR = 21
    """Tiltrotor VTOL."""

    VTOL_FIXEDROTOR = 22
    """VTOL with separate fixed rotors."""

    VTOL_TAILSITTER = 23
    """Tailsitter VTOL."""

    VTOL_TILTWING = 24
    """Tiltwing VTOL."""

    VTOL_RESERVED5 = 25
    """Reserved VTOL type."""

    GIMBAL = 26
    """Gimbal."""

    ADSB = 27
    """ADSB system."""

    PARAFOIL = 28
    """Steerable, nonrigid airfoil."""

    DODECAROTOR = 29
    """Dodecarotor."""

    CAMERA = 30
    """Camera."""

    CHARGING_STATION = 31
    """Charging station."""

    FLARM = 32
    """FLARM collision avoidance system."""

    SERVO = 33
    """Servo."""

    ODID = 34
    """Open Drone ID."""

    DECAROTOR = 35
    """Decarotor."""

    BATTERY = 36
    """Battery."""

    PARACHUTE = 37
    """Parachute."""

    LOG = 38
    """Log."""

    OSD = 39
    """On-Screen Display (OSD)."""

    IMU = 40
    """Inertial Measurement Unit (IMU)."""

    GPS = 41
    """Global Positioning System (GPS)."""

    WINCH = 42
    """Winch."""

    GENERIC_MULTIROTOR = 43
    """Generic multirotor type."""

    ILLUMINATOR = 44
    """Illuminator, such as a torch or searchlight."""


# undoumented
class AltitudeMode(IntEnum):
    """Enumeration for altitude modes."""

    MIXED = 0
    """Altitude mode can differ for each item."""

    LAUNCH = 1
    """Altitude is relative to the launch position."""

    AMSL = 2
    """Altitude is absolute AMSL (Above Mean Sea Level)."""

    TERRAIN = 3
    """Altitude is relative to the terrain."""
