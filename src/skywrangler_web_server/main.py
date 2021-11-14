import logging

from aiohttp import web

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get("/api/test")
async def handle_test(request: web.Request) -> web.Response:
    return web.json_response({"status": "success"})


@routes.post("/api/shutdown")
async def handle_shutdown(request: web.Request) -> web.Response:
    return web.Response()


def main() -> None:
    app = web.Application()
    app.router.add_routes(routes)

    web.run_app(app)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
