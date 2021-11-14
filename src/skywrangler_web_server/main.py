from aiohttp import web

from .api import routes


def main() -> None:
    app = web.Application()
    app.router.add_routes(routes)

    web.run_app(app)
