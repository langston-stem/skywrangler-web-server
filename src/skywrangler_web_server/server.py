import asyncio
from typing import Optional
import weakref

from aiohttp import web
from aiohttp.typedefs import PathLike
from aiohttp_sse import EventSourceResponse
from sdnotify import SystemdNotifier

from .api import routes
from .drone import Drone
from .rpi import RPi


async def on_startup(app: web.Application) -> None:
    drone: Drone = app["drone"]
    rpi: RPi = app["rpi"]

    await asyncio.gather(drone.async_init(), rpi.async_init())

    # FIXME: how to wait for socket to become ready?
    # Without this delay, nginx will fail to start up because it can't see the
    # server. It would be better if we could find the actual condition to test
    # for instead of using an arbitrary delay.
    asyncio.get_running_loop().call_later(
        10, lambda: SystemdNotifier().notify("READY=1")
    )


async def on_shutdown(app: web.Application) -> None:
    tasks: weakref.WeakSet[asyncio.Future] = app["tasks"]

    for t in tasks:
        t.cancel()


async def root_handler(request):
    """
    Redirects ``/`` to ``/index.html``.
    """
    return web.HTTPFound("/index.html")


def serve(port: Optional[int] = None, static_path: Optional[PathLike] = None) -> None:
    """
    Runs the web server.

    Args:
        static_path: optional path to directory containing static files to
            be served.
    """
    app = web.Application()

    app.router.add_routes(routes)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # If a path is given, serve static content, e.g the web client.
    # NB: since this uses the root path, it needs to go after all other routes.
    if static_path:
        app.router.add_route("*", "/", root_handler)
        app.router.add_static("/", static_path)

    # track "forever" tasks so we can cancel on shutdown
    app["tasks"] = weakref.WeakSet()

    app["drone"] = Drone()
    app["rpi"] = RPi()

    web.run_app(app, port=port)
