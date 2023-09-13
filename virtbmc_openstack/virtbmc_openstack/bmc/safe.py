from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from virtbmc_core.constants import IPMI_COMPLETION_CODES as CODE
from virtbmc_openstack.bmc import BaseOpenStackBMC

if TYPE_CHECKING:
    from typing import Literal


log: logging.Logger = logging.getLogger(__name__)


class SafeBMC(BaseOpenStackBMC):
    mode: str = "safe"

    def is_active(self) -> bool:
        log.debug("is_active: called")
        self._refresh_server_state()

        return (
            self.server.status == "ACTIVE"
            and self.server.task_state is None
            or self.server.task_state == "powering-on"
        )

    def get_power_state(self) -> Literal["on", "off"]:
        log.debug("get_power_state: called")
        return "on" if self.is_active() else "off"

    def power_off(self) -> int:
        log.debug("power_off: called")
        self._refresh_server_state()

        if (
            self.server.status == "SHUTOFF"
            and self.server.task_state is None
            or self.server.task_state == "powering-off"
        ):
            return CODE.SUCCESS

        if self.server.task_state:
            return CODE.NODE_BUSY

        if self.server.status == "ACTIVE":
            self.server.stop(self.conn.compute)
            return CODE.SUCCESS

        return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

    def power_on(self, refresh: bool = True) -> int:
        log.debug("power_on: called")
        if refresh:
            self._refresh_server_state()

        if self.is_active():
            return CODE.SUCCESS

        if self.server.task_state:
            return CODE.NODE_BUSY

        if self.server.status in ["SHUTOFF", "STOPPED"]:
            self.server.start(self.conn.compute)
            return CODE.SUCCESS

        return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

    def power_reset(self) -> int:
        log.debug("power_reset: called")
        self._refresh_server_state()

        if self.server.status == "REBOOT":
            return CODE.SUCCESS

        if self.server.task_state:
            if self.server.task_state in ["rebooting", "reboot_started"]:
                return CODE.SUCCESS

            return CODE.NODE_BUSY

        if self.server.status in ["SHUTOFF", "STOPPED"]:
            return self.power_on(refresh=False)

        if self.server.status == "ACTIVE":
            self.server.reboot(self.conn.compute, reboot_type="SOFT")
            return CODE.SUCCESS

        return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

    def power_cycle(self) -> int:
        log.debug("power_cycle: called")
        self._refresh_server_state()

        if self.server.status == "HARD_REBOOT":
            return CODE.SUCCESS

        if self.server.task_state:
            if self.server.task_state in ["rebooting_hard", "reboot_started_hard"]:
                return CODE.SUCCESS

            return CODE.NODE_BUSY

        if self.server.status in ["SHUTOFF", "STOPPED"]:
            return self.power_on(refresh=False)

        if self.server.status == "ACTIVE":
            self.server.reboot(self.conn.compute, reboot_type="HARD")

            return CODE.SUCCESS

        return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

    def power_shutdown(self) -> int:
        # Should attempt a clean shutdown but openstack doesn't know the difference
        log.debug("power_shutdown: called")

        self.power_off()
        return CODE.SUCCESS
