from aiohttp import web

routes = web.RouteTableDef()


@routes.get("/api/test")
async def handle_test(request: web.Request) -> web.Response:
    return web.json_response({"status": "success"})


@routes.post("/api/shutdown")
async def handle_shutdown(request: web.Request) -> web.Response:
    return web.Response()
