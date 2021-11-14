from aiohttp import web

from .api import routes
from .rpi import RPi


def main() -> None:
    app = web.Application()
    app.router.add_routes(routes)
    app["rpi"] = RPi()

    web.run_app(app)
