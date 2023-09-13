from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Dict

import openstack

from virtbmc_core import Bmc

if TYPE_CHECKING:
    from logging import Logger
    from typing import Literal, Optional, Union

    from openstack.compute.v2.server import Server
    from openstack.connection import Connection

    # fmt: off
    status = Literal[
        "ACTIVE", "BUILDING", "DELETED", "ERROR", "HARD_REBOOT", "PASSWORD",
        "PAUSED", "REBOOT", "REBUILD", "RESCUED", "RESIZED", "REVERT_RESIZE",
        "SHUTOFF", "SOFT_DELETED", "STOPPED", "SUSPENDED", "UNKNOWN",
        "VERIFY_RESIZE"]
    # fmt: on

log: Logger = logging.getLogger(__name__)


class BaseOpenStackBMC(Bmc):
    driver: str = "openstack"
    server: Server
    conn: Connection

    def __init__(
        self,
        name: str,
        mode: str,
        cloud: Optional[str] = None,
        username: str = "admin",
        password: str = "password",
        port: int = 623,
        address: str = "::",
    ) -> None:
        super().__init__(username, password, port, address)
        self.name = name
        self.cloud = cloud
        self.mode = mode

    def start(self, timeout: int = 30) -> None:
        # TODO: add timeout when connecting for too long
        log.debug("connecting to the cloud")

        self.conn = openstack.connect(cloud=self.cloud)
        server: Optional[Server] = self.conn.compute.find_server(self.name)

        if server is None:
            log.error(f"server: {self.name} not found in the cloud, stopping bmc")
            self.stop()

        else:
            if server.task_state is not None:
                log.warning(
                    f"server: {self.name} task in progress waiting for it to finish"
                )
                self._wait_for_idle()

            self.server = server

            super().start(timeout=timeout)
            log.info(f"{self.name} started with connection to cloud")

    def stop(self) -> None:
        self.conn.close()
        super().stop()

    def config(self) -> Dict[str, Union[str, int, None]]:
        return {"mode": self.mode, **super().config()}

    def _refresh_server_state(self) -> None:
        server = self.conn.compute.get_server(self.server)
        log.debug(
            "Refreshing server status: current server "
            f"status: {self.server.status}; "
            f"vm_state: {self.server.vm_state}; "
            f"task_state: {self.server.task_state};"
        )

        if self.server is None:
            log.error("server stopped existing in meantime, exiting")

            if not self._stopped:
                self.stop()

        self.server = server

    def _wait_for_idle(self, interval: float = 2) -> None:
        while self.server.task_state:
            self._refresh_server_state()

            if self.server.task_state is not None:
                time.sleep(interval)

    # BMC Operations
    # ref: 28.3 Chassis Control Command: https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-intelligent-platform-mgt-interface-spec-2nd-gen-v2-0-spec-update.pdf
    def cold_reset(self) -> int:
        log.debug("cold_reset: caleld, stopping BMC")
        self.stop()
        return 0

    def get_power_state(self) -> Literal["on", "off"]:
        # TODO: allow returning busy (fix in cached and unsafe), rewrite in virtbmc_core
        log.debug("get_power_state: called")
        return "on" if self.is_active() else "off"
