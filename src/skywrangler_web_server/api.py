import asyncio
import json
import logging
from http import HTTPStatus
from typing import List, TypedDict
import weakref

from aiohttp import web
from aiohttp_sse import EventSourceResponse, sse_response
import rx.core.typing as rx_typing

from .drone import Drone, for_each
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


@routes.get("/api/drone/status")
async def handle_drone_status(request: web.Request) -> web.Response:
    try:
        tasks: weakref.WeakSet[asyncio.Future] = request.app["tasks"]
        drone: Drone = request.app["drone"]
        queue = asyncio.Queue[DroneStatusEvent]()

        response: EventSourceResponse
        async with sse_response(request) as response:

            subscriptions: List[rx_typing.Disposable] = []

            try:
                subscriptions.append(
                    for_each(
                        drone.connection_state,
                        lambda state: queue.put_nowait(
                            DroneStatusEvent(
                                data=json.dumps(state.is_connected), event="isConnected"
                            )
                        ),
                    )
                )
                subscriptions.append(
                    for_each(
                        drone.health_all_ok,
                        lambda ok: queue.put_nowait(
                            DroneStatusEvent(data=json.dumps(ok), event="isHealthAllOk")
                        ),
                    )
                )
                subscriptions.append(
                    for_each(
                        drone.health,
                        lambda health: queue.put_nowait(
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
                        ),
                    )
                )
                subscriptions.append(
                    for_each(
                        drone.in_air,
                        lambda is_in_air: queue.put_nowait(
                            DroneStatusEvent(
                                data=json.dumps(is_in_air), event="isInAir"
                            )
                        ),
                    )
                )
                subscriptions.append(
                    for_each(
                        drone.status_text,
                        lambda status: queue.put_nowait(
                            DroneStatusEvent(
                                data=json.dumps(
                                    {"text": status.text, "type": status.type.name}
                                ),
                                event="statusText",
                            )
                        ),
                    )
                )

                # have to wrap this in a task to allow cancellation for proper
                # server shutdown
                async def process_queue():
                    while True:
                        event = await queue.get()
                        await response.send(**event)

                task = asyncio.create_task(process_queue())
                tasks.add(task)
                await task

            finally:
                for s in subscriptions:
                    s.dispose()

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
