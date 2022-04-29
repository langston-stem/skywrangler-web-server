import asyncio
import logging
from typing import Optional

from mavsdk import System

# causes spurious errors
del System.__del__

logger = logging.getLogger(__name__)


class Drone:
    system: System
    _mission_task: Optional[asyncio.Task]

    def __init__(self):
        self.system = System(mavsdk_server_address="localhost")
        self._mission_task = None

    async def async_init(self) -> None:
        """
        Performs async initialization.
        """
        await self.system.connect()

    async def _fly_mission(self) -> None:
        # TODO: connection check?
        # TODO: health check?
        logger.info("arming...")
        await self.system.action.arm()
        logger.info("taking off...")
        await self.system.action.takeoff()
        logger.info("flying...")
        await asyncio.sleep(30)
        logger.info("returning...")
        await self.system.action.return_to_launch()

        async for armed in self.system.telemetry.armed():
            logger.debug(f"armed: {armed}")
            if not armed:
                break

        logger.info("disarmed")

    async def fly_mission(self) -> None:
        if self._mission_task:
            raise RuntimeError("mission already in progress")

        self._mission_task = asyncio.create_task(self._fly_mission())

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
