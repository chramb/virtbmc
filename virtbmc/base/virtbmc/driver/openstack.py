from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

import openstack
from openstack.compute.v2.server import Server
from openstack.connection import Connection
from virtbmc.driver.base import BaseBMC

if TYPE_CHECKING:
    from typing import Dict, Literal, Union

    # fmt: off
    status = Literal[
        "ACTIVE", "BUILDING", "DELETED", "ERROR", "HARD_REBOOT", "PASSWORD", 
        "PAUSED", "REBOOT", "REBUILD", "RESCUED", "RESIZED", "REVERT_RESIZE", 
        "SHUTOFF", "SOFT_DELETED", "STOPPED", "SUSPENDED", "UNKNOWN", 
        "VERIFY_RESIZE"]
    # fmt: on

log = logging.getLogger("virtbmc.driver.dummy")
# connection_args: Dict[str, str] = {"app_name": "VirtBMC", "app_version": "0.4"}


class OpenStackBMC(BaseBMC):
    cloud: str
    name: str
    driver: str = field(default="openstack", init=False)
    server: Server = field(init=False, repr=False)

    def start(self):
        with openstack.connect(self.cloud) as conn:
            server: Union[Server, None] = conn.compute.find_server(self.name)
        if server is None:
            raise Exception(f"Server with name {self.name} not found")
        super().start()

    def _check_server_missing(self, server: Optional[Server]):
        if server is None:
            raise Exception("server stopped existing in meantime")

    def _wait_util_power_status(self, status: status, interval: float = 5) -> None:
        while self.server.status != status and self._started:
            # refresh server instance
            with openstack.connect(self.cloud) as conn:
                server: Union[Server, None] = conn.compute.get_server(self.server)

            if server is None:
                raise Exception("server stopped existing in meantime")

            time.sleep(interval)
        return

    # BMC Operations
    # ref: 28.3 Chassis Control Command: https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-intelligent-platform-mgt-interface-spec-2nd-gen-v2-0-spec-update.pdf
    def cold_reset(self):
        self.stop()
        return 0

    def is_active(self):
        with openstack.connect(self.cloud) as conn:
            conn.compute.get_server(self.server)
            return self.server.status == "ACTIVE"

    def get_power_state(self):
        with openstack.connect(self.cloud) as conn:
            self.server = conn.compute.get_server(self.server)
            #     "off": 0,
            #     "on": 1,
            self._check_server_missing(self.server)

            return "on" if self.server.status == "ACTIVE" else "off"

    def power_off(self):
        # this should be power down without waiting for clean shutdown
        with openstack.connect(self.cloud) as conn:
            conn.compute.stop_server(self.server)

    def power_on(self):
        with openstack.connect(self.cloud) as conn:
            conn.compute.start_server(self.server)

    def power_reset(self):
        with openstack.connect(self.cloud) as conn:
            conn.compute.reboot_server(self.server, reboot_type="SOFT")

    def power_shutdown(self):
        # Should attempt a clean shutdown
        with openstack.connect(self.cloud) as conn:
            conn.compute.stop_server(self.server)
