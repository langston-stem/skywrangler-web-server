import logging

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType
from dbus_next.introspection import Node

logger = logging.getLogger(__name__)


class RPi:
    """
    Class for interacting with a Raspberry Pi computer
    """

    @property
    def _avahi_server_xml(self) -> Node:
        with open("/usr/share/dbus-1/interfaces/org.freedesktop.Avahi.Server.xml") as f:
            return Node.parse(f.read())

    @property
    def _avahi_entry_group_xml(self) -> Node:
        with open(
            "/usr/share/dbus-1/interfaces/org.freedesktop.Avahi.EntryGroup.xml"
        ) as f:
            return Node.parse(f.read())

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

        # register server with avahi
        obj = self._bus.get_proxy_object(
            "org.freedesktop.Avahi", "/", self._avahi_server_xml
        )
        avahi_server = obj.get_interface("org.freedesktop.Avahi.Server")
        entry_path = await avahi_server.call_entry_group_new()
        obj = self._bus.get_proxy_object(
            "org.freedesktop.Avahi", entry_path, self._avahi_entry_group_xml
        )
        entry_group = obj.get_interface("org.freedesktop.Avahi.EntryGroup")
        await entry_group.call_add_service(
            -1,  # AVAHI_IF_UNSPEC
            -1,  # AVAHI_PROTO_UNSPEC
            0,  # flags
            "Sky Wrangler UAV",  # name
            "_http._tcp",  # type
            "",  # domain
            "",  # host
            80,  # port
            [],  # txt
        )
        await entry_group.call_commit()

    async def shutdown(self) -> None:
        await self._login_manager.call_power_off(False)
