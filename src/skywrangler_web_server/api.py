from http import HTTPStatus

from aiohttp import web

from .rpi import RPi

routes = web.RouteTableDef()


@routes.get("/api/test")
async def handle_test(request: web.Request) -> web.Response:
    return web.json_response({"status": "success"})


@routes.post("/api/shutdown")
async def handle_shutdown(request: web.Request) -> web.Response:
    try:
        rpi: RPi = request.app["rpi"]
        rpi.shutdown()
        return web.Response()
    except Exception as ex:
        return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, reason=str(ex))
