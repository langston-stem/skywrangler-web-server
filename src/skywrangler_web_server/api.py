import asyncio
import json
import logging
from http import HTTPStatus
from typing import TypedDict
import weakref

from aiohttp import web
from aiohttp_sse import EventSourceResponse, sse_response

from .drone import Drone
from .rpi import RPi

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


async def send_heartbeat(response: EventSourceResponse) -> None:
    while True:
        await response.send("", event="heartbeat")
        await asyncio.sleep(10)


@routes.get("/api/status")
async def handle_status(request: web.Request) -> web.Response:
    try:
        tasks: weakref.WeakSet[asyncio.Future] = request.app["tasks"]

        response: EventSourceResponse
        async with sse_response(request) as response:

            task = asyncio.create_task(send_heartbeat(response))

            tasks.add(task)

            try:
                await task
            finally:
                tasks.discard(task)

        return response
    except Exception as ex:
        logger.exception("/api/status")
        return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason=str(ex))


@routes.post("/api/shutdown")
async def handle_shutdown(request: web.Request) -> web.Response:
    try:
        rpi: RPi = request.app["rpi"]
        await rpi.shutdown()
        return web.Response()
    except Exception as ex:
        logger.exception("/api/shutdown")
        return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason=str(ex))


class DroneStatusEvent(TypedDict):
    data: str
    event: str


async def monitor_is_connected(drone: Drone, queue: asyncio.Queue[DroneStatusEvent]):
    """
    Subscribes to drone connection_state events.

    Args:
        drone: The drone instance.
        queue: The event queue.
    """
    async for state in drone.system.core.connection_state():
        logger.debug(f"connection_state: {state}")

        await queue.put(
            DroneStatusEvent(data=json.dumps(state.is_connected), event="isConnected")
        )


async def monitor_is_all_health_ok(
    drone: Drone, queue: asyncio.Queue[DroneStatusEvent]
):
    """
    Subscribes to drone is_health_all_ok events.

    Args:
        drone: The drone instance.
        queue: The event queue.
    """
    async for ok in drone.system.telemetry.health_all_ok():
        logger.debug(f"health_all_ok: {ok}")

        await queue.put(DroneStatusEvent(data=json.dumps(ok), event="isHealthAllOk"))


async def monitor_health(drone: Drone, queue: asyncio.Queue[DroneStatusEvent]):
    """
    Subscribes to drone health events.

    Args:
        drone: The drone instance.
        queue: The event queue.
    """
    async for health in drone.system.telemetry.health():
        logger.debug(f"health: {health}")

        await queue.put(
            DroneStatusEvent(
                data=json.dumps(
                    {
                        "isAccelerometerCalibrationOk": health.is_accelerometer_calibration_ok,
                        "isArmable": health.is_armable,
                        "isGlobalPositionOk": health.is_global_position_ok,
                        "isGyrometerCalibrationOk": health.is_gyrometer_calibration_ok,
                        "isHomePositionOk": health.is_home_position_ok,
                        "isLocalPositionOk": health.is_local_position_ok,
                        "isMagnetometerCalibrationOk": health.is_magnetometer_calibration_ok,
                    }
                ),
                event="health",
            )
        )


async def monitor_in_air(drone: Drone, queue: asyncio.Queue[DroneStatusEvent]):
    """
    Subscribes to drone in_air events.

    Args:
        drone: The drone instance.
        queue: The event queue.
    """
    async for is_in_air in drone.system.telemetry.in_air():
        logger.debug(f"is_in_air: {is_in_air}")

        await queue.put(DroneStatusEvent(data=json.dumps(is_in_air), event="isInAir"))


async def monitor_status_text(drone: Drone, queue: asyncio.Queue[DroneStatusEvent]):
    """
    Subscribes to drone status_text events.

    Args:
        drone: The drone instance.
        queue: The event queue.
    """
    async for text in drone.system.telemetry.status_text():
        logger.info(f"status_text: {text}")

        await queue.put(
            DroneStatusEvent(
                data=json.dumps({"text": text.text, "type": text.type.name}),
                event="statusText",
            )
        )


@routes.get("/api/drone/status")
async def handle_drone_status(request: web.Request) -> web.Response:
    try:
        tasks: weakref.WeakSet[asyncio.Future] = request.app["tasks"]
        drone: Drone = request.app["drone"]
        queue = asyncio.Queue[DroneStatusEvent]()

        response: EventSourceResponse
        async with sse_response(request) as response:

            async def process_queue():
                while True:
                    event = await queue.get()
                    await response.send(**event)

            task = asyncio.gather(
                process_queue(),
                monitor_is_connected(drone, queue),
                monitor_is_all_health_ok(drone, queue),
                monitor_health(drone, queue),
                monitor_in_air(drone, queue),
                monitor_status_text(drone, queue),
            )

            tasks.add(task)

            try:
                await task
            finally:
                tasks.discard(task)

        return response
    except Exception as ex:
        logger.exception("/api/drone/status")
        return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason=str(ex))


@routes.post("/api/drone/fly_mission")
async def handle_drone_fly_mission(request: web.Request) -> web.Response:
    try:
        mission_parameters = await request.json()
        logger.info("requested mission with: %s", mission_parameters)
        drone: Drone = request.app["drone"]
        # TODO: use sse to send progress updates
        await drone.fly_mission(mission_parameters)
        return web.Response()
    except Exception as ex:
        logger.exception("/api/drone/fly_mission")
        return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason=str(ex))


@routes.post("/api/drone/return")
async def handle_drone_return(request: web.Request) -> web.Response:
    try:
        drone: Drone = request.app["drone"]
        await drone.return_to_launch()
        return web.Response()
    except Exception as ex:
        logger.exception("/api/drone/return")
        return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason=str(ex))
