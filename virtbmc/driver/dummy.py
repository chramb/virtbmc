from __future__ import annotations

import logging
import struct
import uuid
from typing import TYPE_CHECKING, Any

from pyghmi.ipmi.command import power_states
from pyghmi.ipmi.console import ServerConsole

from virtbmc.core import Bmc
from virtbmc.core.constants import IPMI_COMPLETION_CODES as CODE

if TYPE_CHECKING:
    from typing import Literal, Optional

    from pyghmi.ipmi.console import Console
    from pyghmi.ipmi.private.serversession import ServerSession

    from virtbmc.core.types import IPMIRequest, ipmi_boot_device


class DummyBMC(Bmc):
    """Dummy BMC implementation."""

    driver: str = "dummy"

    def __init__(
        self,
        name: str | None = None,
        *,
        username: str | None = None,
        password: str | None = None,
        port: int | None = None,
        address: str | None = None,
        properties: dict[str, Any] = {},
        log: logging.Logger | None = None,
        **kwargs: Any,
    ) -> None:
        self._powerstate: int = 0  # 0: off 1: on
        self._boot_device: ipmi_boot_device = "default"
        self._sol: Optional[Console] = None
        self.log: logging.Logger

        name = name or str(uuid.uuid4())
        self.log = log or logging.getLogger("virtbmc.driver.dummy")

        super().__init__(
            **{
                "name": name,
                "username": username,
                "password": password,
                "port": port,
                "address": address,
                "properties": properties,
                "log": log,
            },
            **kwargs,
        )

    def get_boot_device(self) -> ipmi_boot_device:
        return self._boot_device

    def set_boot_device(self, bootdevice: ipmi_boot_device) -> None:
        self._boot_device = bootdevice

    def cold_reset(self) -> CODE:
        self.stop()
        return CODE.SUCCESS

    def power_off(self) -> CODE:
        self._powerstate = power_states["off"]
        return CODE.SUCCESS

    def power_on(self) -> CODE:
        self._powerstate = power_states["on"]
        return CODE.SUCCESS

    def power_cycle(self) -> CODE:
        return CODE.SUCCESS

    def power_reset(self) -> CODE:
        return CODE.SUCCESS

    def pulse_diag(self) -> CODE:
        return CODE.SUCCESS

    def power_shutdown(self) -> CODE:
        self.power_off()
        return CODE.SUCCESS

    def get_power_state(self) -> Literal["on", "off"]:  # TODO: remove this
        return "on" if self._powerstate else "off"

    def is_active(self) -> bool:
        return self._powerstate == power_states["on"]

    def activate_payload(self, request: IPMIRequest, session: ServerSession) -> None:
        if self.iohandler is None or not self.is_active():  # type: ignore
            session.send_ipmi_response(code=0x81)  # type: ignore
        elif self.activated:
            session.send_ipmi_response(code=0x80)  # type: ignore
        else:
            self.activated = True
            solport = list(struct.unpack("BB", struct.pack("!H", self.port)))
            session.send_ipmi_response(data=[0, 0, 0, 0, 1, 0, 1, 0, *solport, 255, 255])  # type: ignore
            self.sol = ServerConsole(session, self.iohandler)

    def deactivate_payload(self, request: IPMIRequest, session: ServerSession) -> None:
        if self.iohandler is None:  # type: ignore
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
        self.log.info(data)
        if data == b"\r" and self.sol:
            self.sol.send_data(b"\033[1B\033[80D")  # type: ignore
        elif self.sol:
            self.sol.send_data(data)  # type: ignore


if __name__ == "__main__":
    import sys

    log = logging.getLogger(__package__)
    log.setLevel(logging.INFO)
    prog = "python -m virtbmc.driver.dummy" if sys.argv[0][-11:] == "dummy.py" else "virtbmc-dummy"

    bmc = None
    try:
        bmc = DummyBMC(log=log)
        log.info("bmc started")
        bmc.start()

    except KeyboardInterrupt:
        if bmc:
            bmc.stop()
            log.info("bmc stopped")
        print("Interrupt received. Exiting.")
