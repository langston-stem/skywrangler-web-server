from typing import Optional
from aiohttp import web
from aiohttp.typedefs import PathLike

from .api import routes
from .rpi import RPi


async def root_handler(request):
    """
    Redirects ``/`` to ``/index.html``.
    """
    return web.HTTPFound("/index.html")


def serve(static_path: Optional[PathLike] = None) -> None:
    """
    Runs the web server.

    Args:
        static_path: optional path to directory containing static files to
            be served.
    """
    app = web.Application()

    app.router.add_routes(routes)

    # If a path is given, serve static content, e.g the web client.
    # NB: since this uses the root path, it needs to go after all other routes.
    if static_path:
        app.router.add_route("*", "/", root_handler)
        app.router.add_static("/", static_path)

    app["rpi"] = RPi()

    web.run_app(app)
