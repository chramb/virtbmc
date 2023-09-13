from __future__ import annotations

import logging

import openstack.exceptions

from virtbmc_core.constants import IPMI_COMPLETION_CODES as CODE
from virtbmc_openstack.bmc import BaseOpenStackBMC

log = logging.getLogger(__name__)


class SimpleBMC(BaseOpenStackBMC):
    driver: str = "openstack"
    mode: str = "simple"

    def is_active(self) -> bool:
        self._refresh_server_state()
        return self.server.status == "ACTIVE"

    def power_off(self) -> int:
        try:
            self.server.stop(self.conn.compute)
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException:
            return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

    def power_on(self, refresh: bool = True) -> int:
        try:
            self.server.start(self.conn.compute)
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException:
            return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

    def power_reset(self, reboot_type: str = "SOFT") -> int:
        try:
            self.server.reboot(self.conn.compute, reboot_type)
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException:
            return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

    def power_cycle(self) -> int:
        return self.power_reset(reboot_type="HARD")

    def power_shutdown(self) -> int:
        return self.power_off()
