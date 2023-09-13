from __future__ import annotations

import logging
from threading import Thread
from typing import Any, Callable

from virtbmc_core.constants import IPMI_COMPLETION_CODES as CODE
from virtbmc_openstack.bmc import BaseOpenStackBMC

log: logging.Logger = logging.getLogger(__name__)


class UnsafeBMC(BaseOpenStackBMC):
    mode: str = "unsafe"
    task: Thread = Thread(name="")

    def is_active(self) -> bool:
        return self.server.status == "ACTIVE"

    def wrap_unsafe(  # type: ignore[no-untyped-def]
        self, cmd: Callable[[Any], Any], *args, **kwargs  # noqa ANN002
    ) -> None:
        try:
            cmd(*args, **kwargs)
        except Exception as e:
            log.error(f"encountered issue {e}")
            self._wait_for_idle()

    def power_off(self) -> int:
        if self.task.is_alive():
            if self.task.name == "power_off":
                return CODE.SUCCESS
            else:
                return CODE.NODE_BUSY

        if self.server.status == "SHUTOFF":
            return CODE.SUCCESS

        task = Thread(
            name="power_off",
            target=self.wrap_unsafe,
            args=(self.server.stop, self.conn.compute),
        )
        task.start()
        self.server.status = "SHUTOFF"
        return CODE.SUCCESS

    def power_on(self) -> int:
        if self.task.is_alive():
            if self.task.name == "power_on":
                return CODE.SUCCESS
            else:
                return CODE.NODE_BUSY

        if self.server.status == "ACTIVE":
            return CODE.SUCCESS

        task = Thread(
            name="power_on",
            target=self.wrap_unsafe,
            args=(self.server.start, self.conn.compute),
        )
        task.start()
        self.server.status = "ACTIVE"
        return CODE.SUCCESS

    def power_reset(self) -> int:
        if self.task.is_alive():
            if self.task.name == "power_reset":
                return CODE.SUCCESS
            return CODE.NODE_BUSY

        if self.server.status == "SHUTOFF":
            return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

        self.task = Thread(
            name="power_reset",
            target=self.wrap_unsafe,
            args=(self.server.reboot, self.conn.compute, "SOFT"),
        )
        self.task.start()

        return CODE.SUCCESS

    def power_cycle(self) -> int:
        if self.task.is_alive():
            if self.task.name == "power_cycle":
                return CODE.SUCCESS
            else:
                return CODE.NODE_BUSY

        if self.server.status == "SHUTOFF":
            return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

        self.task = Thread(
            name="power_cycle",
            target=self.wrap_unsafe,
            args=(self.server.reboot, self.conn.compute, "HARD"),
        )
        self.task.start()

        return CODE.SUCCESS

    def power_shutdown(self) -> int:
        return self.power_off()
