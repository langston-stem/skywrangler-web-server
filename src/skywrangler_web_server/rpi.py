import logging

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType

logger = logging.getLogger(__name__)


class RPi:
    """
    Class for interacting with a Raspberry Pi computer
    """

    # TODO: add __init__ that checks that this is actually running on an RPi

    async def async_init(self) -> None:
        """
        Performs async init (since it can't be done in __init__()).
        """
        # set up D-bus
        self._bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

        introspection = await self._bus.introspect(
            "org.freedesktop.login1", "/org/freedesktop/login1"
        )
        obj = self._bus.get_proxy_object(
            "org.freedesktop.login1", "/org/freedesktop/login1", introspection
        )
        self._login_manager = obj.get_interface("org.freedesktop.login1.Manager")

    async def shutdown(self) -> None:
        await self._login_manager.call_power_off(False)
