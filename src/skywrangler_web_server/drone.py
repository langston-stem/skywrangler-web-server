import asyncio
import logging
from typing import NamedTuple, Optional

from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan

from .geo import origin_alt_to_takeoff_alt, dist_ang_to_horiz_vert

# causes spurious errors
del System.__del__

logger = logging.getLogger(__name__)

SAFE_ALTITUDE = 30  # meters


class Origin(NamedTuple):
    """
    The origin point - i.e. the center of the enclosure.
    """

    latitude: float
    longitude: float
    elevation: float


class Parameters(NamedTuple):
    """
    The experiment parameters (variables).
    """

    speed: float
    distance: float
    angle: float


class Drone:
    system: System
    _mission_task: Optional[asyncio.Task]

    def __init__(self):
        self.system = System(mavsdk_server_address="localhost")
        self._mission_task = None

        # This will block forever if there is no autopilot detected, so we run
        # it in a background task so the server doesn't fail to start when
        # there is no autopilot connected.
        logger.info("waiting for drone connection...")
        asyncio.create_task(self.system.connect()).add_done_callback(
            lambda t: logger.info("drone connected")
        )

    async def _fly_mission(self, origin: Origin, parameters: Parameters) -> None:
        # TODO: connection check?
        # TODO: health check?
        # TODO: use origin/parameters to create mission plan
        logger.info("starting mission with %r %r", origin, parameters)

        horizontal, vertical = dist_ang_to_horiz_vert(
            parameters.distance, parameters.angle
        )
        async for position in self.system.telemetry.home():
            break

        mission_items = []
        # Take off to safe altitude
        mission_items.append(
            MissionItem(
                float("nan"),
                float("nan"),
                SAFE_ALTITUDE,
                parameters.speed,
                True,
                float("nan"),
                float("nan"),
                MissionItem.CameraAction.NONE,
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
            )
        )
        # Flies at requested speed and safe altitude to origin point
        mission_items.append(
            MissionItem(
                origin.latitude,
                origin.longitude,
                SAFE_ALTITUDE,
                float("nan"),
                True,
                float("nan"),
                float("nan"),
                MissionItem.CameraAction.NONE,
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
            )
        )
        # descend to vertical atitude above the origin
        mission_items.append(
            MissionItem(
                origin.latitude,
                origin.longitude,
                origin_alt_to_takeoff_alt(
                    vertical, origin.elevation, position.absolute_altitude_m
                ),
                float("nan"),
                True,
                float("nan"),
                float("nan"),
                MissionItem.CameraAction.NONE,
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
            )
        )

        mission_plan = MissionPlan(mission_items)

        logger.info("Uploading mission...")
        await self.system.mission.upload_mission(mission_plan)
        logger.info("arming...")
        await self.system.action.arm()
        logger.info("Starting mission...")
        await self.system.mission.start_mission()

        # wait for drone to be disarmed to assume it has landed
        async for armed in self.system.telemetry.armed():
            logger.debug(f"armed: {armed}")
            if not armed:
                break

        logger.info("disarmed")

    async def fly_mission(self, mission_parameters) -> None:
        if self._mission_task:
            raise RuntimeError("mission already in progress")

        # TODO: validate parameters
        origin = Origin(
            mission_parameters["origin"]["latitude"],
            mission_parameters["origin"]["longitude"],
            mission_parameters["origin"]["elevation"],
        )
        parameters = Parameters(
            mission_parameters["parameters"]["speed"],
            mission_parameters["parameters"]["distance"],
            mission_parameters["parameters"]["angle"],
        )

        self._mission_task = asyncio.create_task(self._fly_mission(origin, parameters))

        try:
            await self._mission_task
        finally:
            self._mission_task = None

    async def return_to_launch(self) -> None:
        if self._mission_task:
            logger.debug("canceling mission")
            self._mission_task.cancel()

        logger.info("returing to launch site...")
        await self.system.action.return_to_launch()


async def test():
    drone = Drone()

    await drone.async_init()
    await drone.fly_mission()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test())
