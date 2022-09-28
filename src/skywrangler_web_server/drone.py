import asyncio
import logging
from typing import NamedTuple, Optional

from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan

# causes spurious errors
del System.__del__

logger = logging.getLogger(__name__)


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

        mission_items = []
        mission_items.append(
            MissionItem(
                origin.latitude,
                origin.longitude,
                25,
                10,
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
