import asyncio
import json
import logging
from http import HTTPStatus
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


async def monitor_is_connected(
    drone: Drone, response: EventSourceResponse, lock: asyncio.Lock
):
    """
    Subscribes to drone connection_state events.

    Args:
        drone: The drone instance.
        resposne: The SSE response.
        lock: Prevents concurrent ``response.send()`` calls.
    """
    async for state in drone.system.core.connection_state():
        logger.debug(f"connection_state: {state}")

        async with lock:
            await response.send(json.dumps(state.is_connected), "is_connected")


async def monitor_is_all_health_ok(
    drone: Drone, response: EventSourceResponse, lock: asyncio.Lock
):
    """
    Subscribes to drone is_health_all_ok events.

    Args:
        drone: The drone instance.
        resposne: The SSE response.
        lock: Prevents concurrent ``response.send()`` calls.
    """
    async for ok in drone.system.telemetry.health_all_ok():
        logger.debug(f"health_all_ok: {ok}")

        async with lock:
            await response.send(json.dumps(ok), "is_health_all_ok")

        # this one updates quite frequently, so rate limit it
        await asyncio.sleep(1)


async def monitor_health(
    drone: Drone, response: EventSourceResponse, lock: asyncio.Lock
):
    """
    Subscribes to drone health events.

    Args:
        drone: The drone instance.
        resposne: The SSE response.
        lock: Prevents concurrent ``response.send()`` calls.
    """
    async for health in drone.system.telemetry.health():
        logger.debug(f"health: {health}")

        async with lock:
            await response.send(
                json.dumps(
                    {
                        "is_accelerometer_calibration_ok": health.is_accelerometer_calibration_ok,
                        "is_armable": health.is_armable,
                        "is_global_position_ok": health.is_global_position_ok,
                        "is_gyrometer_calibration_ok": health.is_gyrometer_calibration_ok,
                        "is_home_position_ok": health.is_home_position_ok,
                        "is_local_position_ok": health.is_local_position_ok,
                        "is_magnetometer_calibration_ok": health.is_magnetometer_calibration_ok,
                    }
                ),
                "health",
            )


async def monitor_in_air(
    drone: Drone, response: EventSourceResponse, lock: asyncio.Lock
):
    """
    Subscribes to drone in_air events.

    Args:
        drone: The drone instance.
        resposne: The SSE response.
        lock: Prevents concurrent ``response.send()`` calls.
    """
    async for is_in_air in drone.system.telemetry.in_air():
        logger.debug(f"is_in_air: {is_in_air}")

        async with lock:
            await response.send(json.dumps(is_in_air), "is_in_air")


async def monitor_status_text(
    drone: Drone, response: EventSourceResponse, lock: asyncio.Lock
):
    """
    Subscribes to drone status_text events.

    Args:
        drone: The drone instance.
        resposne: The SSE response.
        lock: Prevents concurrent ``response.send()`` calls.
    """
    async for text in drone.system.telemetry.status_text():
        logger.debug(f"status_text: {text}")

        async with lock:
            await response.send(json.dumps(text.text), "status_text")


@routes.get("/api/drone/status")
async def handle_drone_status(request: web.Request) -> web.Response:
    try:
        tasks: weakref.WeakSet[asyncio.Future] = request.app["tasks"]
        drone: Drone = request.app["drone"]

        lock = asyncio.Lock()

        response: EventSourceResponse
        async with sse_response(request) as response:

            task = asyncio.gather(
                monitor_is_connected(drone, response, lock),
                monitor_is_all_health_ok(drone, response, lock),
                monitor_health(drone, response, lock),
                monitor_in_air(drone, response, lock),
                monitor_status_text(drone, response, lock),
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
async def handle_shutdown(request: web.Request) -> web.Response:
    try:
        drone: Drone = request.app["drone"]
        # TODO: use sse to send progress updates
        await drone.fly_mission()
        return web.Response()
    except Exception as ex:
        logger.exception("/api/drone/fly_mission")
        return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason=str(ex))


@routes.post("/api/drone/return")
async def handle_shutdown(request: web.Request) -> web.Response:
    try:
        drone: Drone = request.app["drone"]
        await drone.return_to_launch()
        return web.Response()
    except Exception as ex:
        logger.exception("/api/drone/return")
        return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason=str(ex))
