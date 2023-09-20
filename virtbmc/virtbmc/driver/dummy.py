from __future__ import annotations

import logging
import struct
import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from pyghmi.ipmi.command import boot_devices, power_states
from pyghmi.ipmi.console import ServerConsole

from virtbmc_core import Bmc
from virtbmc_core.constants import IPMI_COMPLETION_CODES as CODE
from virtbmc_core.log import log_format

log: logging.Logger = logging.getLogger(__package__)
log_format(log)
log.setLevel(logging.INFO)

if TYPE_CHECKING:
    from argparse import Namespace
    from typing import Literal, Optional, Union

    from pyghmi.ipmi.console import Console
    from pyghmi.ipmi.private.serversession import ServerSession

    from virtbmc_core.bmc import ActionsContainer

    # fmt: off
    _bd_keys = Literal['net', 'network', 'pxe', 'hd', 'safe', 'cd', 'cdrom', 'optical',
                       'dvd', 'floppy', 'usb', 'default', 'setup', 'bios', 'f1',
                       1, 2, 3, 5, 6, 15, 0]
    _bd_vals = Literal['net', 'network', 'pxe', 'hd', 'safe', 'cd', 'cdrom', 'optical',
                       'dvd', 'floppy', 'usb', 'default', 'setup', 'bios', 'f1',
                       'network', 'hd', 'safe', 'optical', 'setup', 'floppy', 'default']
    # fmt: on
    class Request(TypedDict):
        netfn: int
        command: int
        data: bytearray


def uuid4_str() -> str:
    return str(uuid.uuid4)


@dataclass
class DummyBMC(Bmc):
    """Dummy BMC implementation."""

    driver: str = field(init=False, default="dummy")
    name: str = field(default_factory=uuid4_str)
    username: str = "admin"
    password: str = "password"
    address: str = "::"
    port: int = 623
    active: bool = field(init=False, default=False)
    _powerstate: int = 0  # 0: off 1: on
    _boot_device: str = "default"
    _sol: Optional[Console] = None

    @staticmethod
    def cli(parser: ActionsContainer) -> ActionsContainer:
        # fmt: off
        parser.add_argument("name", default=None, action="store", help="Name representing managed object (default: random UUID v4)")  # noqa: E501
        # fmt: on
        return Bmc.cli(parser)

    @staticmethod
    def from_namespace(namespace: Namespace) -> DummyBMC:
        return DummyBMC(
            name=namespace.name,
            address=namespace.address,
            port=namespace.port,
            username=namespace.username,
            password=namespace.password,
        )

    def get_boot_device(self) -> str:
        log.info(f"current boot device: {self._boot_device}")
        return self._boot_device

    def set_boot_device(self, bootdevice: str) -> Union[int, None]:
        device: Optional[_bd_vals] = boot_devices.get(bootdevice, None)
        if bootdevice is None or not isinstance(device, int):
            return CODE.INVALID_DATA_FIELD_IN_REQUEST

        self._boot_device = bootdevice
        log.info(f"boot device set to {self._boot_device}")

    def get_system_guid(self) -> int:
        raise NotImplementedError

    def cold_reset(self) -> int:
        log.info("bmc stopped in response to cold reset command")
        self.stop()
        return 0

    def power_off(self) -> None:
        log.info("power off called")
        time.sleep(10)
        self._powerstate = power_states["off"]
        log.info("device abruptly powered off")

    def power_on(self) -> None:
        self._powerstate = power_states["on"]
        log.info("device powered on")

    def power_cycle(self) -> None:
        log.info("device power cycled")
        pass

    def power_reset(self) -> None:
        log.info("device power reset")
        pass

    def pulse_diag(self) -> int:
        raise NotImplementedError

    def power_shutdown(self) -> None:
        log.info("device cleanly shut down")
        self.power_off()

    def get_power_state(self) -> int:
        return self._powerstate

    def is_active(self) -> int:
        return self._powerstate == power_states["on"]

    def activate_payload(self, request: Request, session: ServerSession) -> None:
        if self.iohandler is None or not self.is_active():
            session.send_ipmi_response(code=0x81)
        elif self.activated:
            session.send_ipmi_response(code=0x80)
        else:
            self.activated = True
            solport = list(struct.unpack("BB", struct.pack("!H", self.port)))
            session.send_ipmi_response(
                data=[0, 0, 0, 0, 1, 0, 1, 0, *solport, 255, 255]
            )
            self.sol = ServerConsole(session, self.iohandler)

    def deactivate_payload(self, request: Request, session: ServerSession) -> None:
        if self.iohandler is None:
            session.send_ipmi_response(code=0x81)
        elif not self.activated:
            session.send_ipmi_response(code=0x80)
        else:
            session.send_ipmi_response()
            if self.sol:
                self.sol.close()
            self.activated = False
            self.sol = None

    def iohandler(self, data: bytes) -> None:
        log.info(data)
        if data == b"\r" and self.sol:
            self.sol.send_data(b"\033[1B\033[80D")
        elif self.sol:
            self.sol.send_data(data)


if __name__ == "__main__":
    from argparse import ArgumentParser, HelpFormatter

    parser = ArgumentParser(
        prog="python -m virtbmc.driver.dummy",
        formatter_class=lambda prog: HelpFormatter(prog, max_help_position=36),
    )
    DummyBMC.cli(parser)
    parsed = parser.parse_args()

    bmc = None
    try:
        bmc = DummyBMC.from_namespace(parsed)
        log.info("bmc started")
        bmc.start()

    except KeyboardInterrupt:
        if bmc:
            bmc.stop()
            log.info("bmc stopped")
        print("Interrupt received. Exiting.")
