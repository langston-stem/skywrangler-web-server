import asyncio
import logging
from typing import AsyncGenerator, Callable, List, Optional, TypeVar, cast

import rx.core.typing as rx_typing
import rx.operators as op
from mavsdk import System
from mavsdk.core import ConnectionState
from mavsdk.mission import MissionItem, MissionPlan, MissionProgress
from mavsdk.telemetry import Battery, GpsInfo, Health, LandedState, Position, StatusText
from rx.core import Observable
from rx.subject import BehaviorSubject, Subject

from .geo import dist_ang_to_horiz_vert, origin_alt_to_takeoff_alt
from .mission import Origin, Parameters, Transect

# causes spurious errors
del System.__del__

logger = logging.getLogger(__name__)

SAFE_ALTITUDE = 30  # meters
NO_VALUE = float("nan")


T = TypeVar("T")


async def monitor_generator(
    observer: rx_typing.Observer[T], generator: Callable[[], AsyncGenerator[T, None]]
):
    async for value in generator():
        observer.on_next(value)


async def wait_one(
    observable: rx_typing.Observable[T],
    *ops: Callable[[rx_typing.Observable[T]], rx_typing.Observable[T]],
) -> T:
    future = asyncio.get_running_loop().create_future()

    def set_result(value):
        if future.get_loop().is_closed():
            return

        future.set_result(value)

    subscription = (
        cast(Observable, observable)
        .pipe(*ops, op.first())
        .subscribe(on_next=set_result)
    )
    try:
        return await future
    finally:
        subscription.dispose()


def for_each(
    observable: rx_typing.Observable[T], func: Callable[[T], None]
) -> rx_typing.Disposable:
    return cast(Observable, observable).subscribe(on_next=func)


class Drone:
    system: System
    _mission_task: Optional[asyncio.Task]

    def __init__(self):
        self.system = System(mavsdk_server_address="localhost")
        self._mission_task = None
        self._subcription_tasks: List[asyncio.Task] = []

        # This will block forever if there is no autopilot detected, so we run
        # it in a background task so the server doesn't fail to start when
        # there is no autopilot connected.
        logger.info("waiting for drone connection...")
        asyncio.create_task(self.system.connect()).add_done_callback(
            self._init_after_connect
        )

    def _init_after_connect(self, _: asyncio.Task):
        logger.info("drone connected")

        self.connection_state: rx_typing.Observable[ConnectionState] = BehaviorSubject(
            False
        )
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(
                    self.connection_state, self.system.core.connection_state
                )
            )
        )

        self.mission_progress: rx_typing.Observable[MissionProgress] = BehaviorSubject(
            False
        )
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(
                    self.mission_progress, self.system.mission.mission_progress
                )
            )
        )

        self.position: rx_typing.Observable[Position] = Subject()
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(self.position, self.system.telemetry.position)
            )
        )

        self.home: rx_typing.Observable[Position] = Subject()
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(self.home, self.system.telemetry.home)
            )
        )

        self.in_air: rx_typing.Observable[bool] = Subject()
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(self.in_air, self.system.telemetry.in_air)
            )
        )

        self.landed_state: rx_typing.Observable[LandedState] = Subject()
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(self.landed_state, self.system.telemetry.landed_state)
            )
        )

        self.armed: rx_typing.Observable[bool] = Subject()
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(self.armed, self.system.telemetry.armed)
            )
        )

        self.gps_info: rx_typing.Observable[GpsInfo] = Subject()
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(self.gps_info, self.system.telemetry.gps_info)
            )
        )

        self.battery: rx_typing.Observable[Battery] = Subject()
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(self.battery, self.system.telemetry.battery)
            )
        )

        self.health: rx_typing.Observable[Health] = Subject()
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(self.health, self.system.telemetry.health)
            )
        )

        self.status_text: rx_typing.Observable[StatusText] = Subject()
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(self.status_text, self.system.telemetry.status_text)
            )
        )

        self.health_all_ok: rx_typing.Observable[bool] = Subject()
        self._subcription_tasks.append(
            asyncio.create_task(
                monitor_generator(
                    self.health_all_ok, self.system.telemetry.health_all_ok
                )
            )
        )

    async def _fly_mission(
        self, origin: Origin, transect: Transect, parameters: Parameters
    ) -> None:
        # TODO: connection check?
        # TODO: health check?
        logger.info("starting mission with %r %r", origin, parameters)

        horizontal, vertical = dist_ang_to_horiz_vert(
            parameters.distance, parameters.angle
        )

        home_position = await wait_one(self.home)

        # mission items need altitudes relative to takeoff altitude
        relative_vertical = origin_alt_to_takeoff_alt(
            vertical, origin.elevation, home_position.absolute_altitude_m
        )

        mission_items = []

        # Take off to safe altitude
        mission_items.append(
            MissionItem(
                latitude_deg=NO_VALUE,
                longitude_deg=NO_VALUE,
                relative_altitude_m=SAFE_ALTITUDE,
                speed_m_s=parameters.speed,
                is_fly_through=True,
                gimbal_pitch_deg=NO_VALUE,
                gimbal_yaw_deg=NO_VALUE,
                camera_action=MissionItem.CameraAction.NONE,
                loiter_time_s=NO_VALUE,
                camera_photo_interval_s=NO_VALUE,
                acceptance_radius_m=NO_VALUE,
                yaw_deg=NO_VALUE,
                camera_photo_distance_m=NO_VALUE,
            )
        )
        # Flies at requested speed and safe altitude to origin point
        mission_items.append(
            MissionItem(
                latitude_deg=origin.latitude,
                longitude_deg=origin.longitude,
                relative_altitude_m=SAFE_ALTITUDE,
                speed_m_s=NO_VALUE,
                is_fly_through=True,
                gimbal_pitch_deg=NO_VALUE,
                gimbal_yaw_deg=NO_VALUE,
                camera_action=MissionItem.CameraAction.NONE,
                loiter_time_s=NO_VALUE,
                camera_photo_interval_s=NO_VALUE,
                acceptance_radius_m=NO_VALUE,
                yaw_deg=NO_VALUE,
                camera_photo_distance_m=NO_VALUE,
            )
        )
        # descend to vertical atitude above the origin
        mission_items.append(
            MissionItem(
                latitude_deg=origin.latitude,
                longitude_deg=origin.longitude,
                relative_altitude_m=relative_vertical,
                speed_m_s=NO_VALUE,
                is_fly_through=False,
                gimbal_pitch_deg=NO_VALUE,
                gimbal_yaw_deg=NO_VALUE,
                camera_action=MissionItem.CameraAction.NONE,
                loiter_time_s=NO_VALUE,
                camera_photo_interval_s=NO_VALUE,
                acceptance_radius_m=0.005,
                yaw_deg=NO_VALUE,
                camera_photo_distance_m=NO_VALUE,
            )
        )

        mission_plan = MissionPlan(mission_items)
        await self.system.mission.set_return_to_launch_after_mission(True)
        logger.info("Uploading mission...")
        await self.system.mission.upload_mission(mission_plan)
        logger.info("arming...")
        await self.system.action.arm()
        logger.info("Starting mission...")
        await self.system.mission.start_mission()

    async def fly_mission(self, mission_parameters) -> None:
        if self._mission_task:
            raise RuntimeError("mission already in progress")

        # TODO: validate parameters
        origin = Origin(
            mission_parameters["origin"]["latitude"],
            mission_parameters["origin"]["longitude"],
            mission_parameters["origin"]["elevation"],
        )
        transect = Transect(
            mission_parameters["transect"]["azimuth"],
            mission_parameters["transect"]["length"],
        )
        parameters = Parameters(
            mission_parameters["parameters"]["speed"],
            mission_parameters["parameters"]["distance"],
            mission_parameters["parameters"]["angle"],
        )

        self._mission_task = asyncio.create_task(
            self._fly_mission(origin, transect, parameters)
        )

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

    async def cancel_all_tasks(self):
        if self._mission_task:
            self._mission_task.cancel()

        for t in self._subcription_tasks:
            t.cancel()

        await asyncio.wait(self._subcription_tasks)


async def test():
    drone = Drone()

    await drone.async_init()
    await drone.fly_mission()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test())
