from __future__ import annotations

import logging
import threading

import openstack
import openstack.exceptions

from virtbmc_core.constants import IPMI_COMPLETION_CODES as CODE
from virtbmc_openstack.bmc import BaseOpenStackBMC

log: logging.Logger = logging.getLogger(__name__)


class CachedBMC(BaseOpenStackBMC):
    driver: str = "openstack"
    mode: str = "cached"
    _refresh_cache: threading.Thread

    def __init__(  # type: ignore[no-untyped-def]
        self, *args, **kwargs  # noqa: ANN002, ANN003
    ) -> None:
        super().__init__(*args, **kwargs)
        # initialize thread in addition to all the normal behaviour
        self._refresh_cache = threading.Thread(target=self._wait_for_idle)

    def is_active(self) -> bool:
        return self.server.status == "ACTIVE"

    def power_off(self) -> int:
        if self._refresh_cache.is_alive():
            return CODE.NODE_BUSY

        if not self.is_active():
            return CODE.SUCCESS

        try:
            self.server.stop(self.conn.compute)
            self.server.status = "SHUTOFF"
            return CODE.SUCCESS

        except openstack.exceptions.ConflictException:
            self._refresh_cache.start()
            return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

    def power_on(self) -> int:
        if self._refresh_cache.is_alive():
            return CODE.NODE_BUSY

        if self.is_active():
            return CODE.SUCCESS

        try:
            self.server.start(self.conn.compute)
            self.server.status = "ACTIVE"
            return CODE.SUCCESS

        except openstack.exceptions.ConflictException:
            self._refresh_cache.start()
            return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

    def power_reset(self, reboot_type: str = "SOFT") -> int:
        if self._refresh_cache.is_alive():
            return CODE.NODE_BUSY

        if not self.is_active():
            return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

        try:
            self.server.reboot(self.conn.compute, reboot_type)
            return CODE.SUCCESS

        except openstack.exceptions.ConflictException:
            self._refresh_cache.start()
            return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

    def power_cycle(self) -> int:
        return self.power_reset(reboot_type="HARD")

    def power_shutdown(self) -> int:
        return self.power_off()
