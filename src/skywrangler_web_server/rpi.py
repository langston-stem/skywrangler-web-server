import logging

logger = logging.getLogger(__name__)


class RPi:
    """
    Class for interacting with a Raspberry Pi computer
    """

    # TODO: add __init__ that checks that this is actually running on an RPi

    def shutdown(self) -> None:
        # TODO: actually shut down the RPi
        logger.info("shut down requested")
