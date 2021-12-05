import asyncio
import logging
from http import HTTPStatus

from aiohttp import web
from aiohttp_sse import sse_response

from .rpi import RPi

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


@routes.get("/api/status")
async def handle_test(request: web.Request) -> web.Response:
    async with sse_response(request) as response:
        while True:
            await response.send("", event="heartbeat")
            await asyncio.sleep(10)

    return response


@routes.post("/api/shutdown")
async def handle_shutdown(request: web.Request) -> web.Response:
    try:
        rpi: RPi = request.app["rpi"]
        await rpi.shutdown()
        return web.Response()
    except Exception as ex:
        return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason=str(ex))
