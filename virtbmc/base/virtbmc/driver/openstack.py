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


@dataclass
class OpenStackBMC(BaseBMC):
    name: str
    cloud: Optional[str] = "__undefined__"
    driver: str = field(default="openstack", init=False)
    server: Server = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.cloud == "__undefined__":
            self.cloud = None
        return super().__post_init__()

    def start(self):
        with openstack.connect(self.cloud) as conn:
            server: Union[Server, None] = conn.compute.find_server(self.name)
        if server is None:
            raise Exception(f"Server with name {self.name} not found")
        super().start()

    def _check_server_missing(self, server: Optional[Server]):
        if server is None:
            raise Exception("server stopped existing in meantime")

    def _ensure_status(self, target_status: status, interval: float = 5) -> None:
        # TODO: somehow handle both active and shutoff if changed
        while self.server.status != target_status and self._started:
            # refresh server instance
            with openstack.connect(self.cloud) as conn:
                server: Union[Server, None] = conn.compute.get_server(self.server)
                if server is None:
                    raise Exception("server stopped existing in meantime")
                if target_status == "SHUTOFF":
                    conn.compute.stop_server(server)
                if target_status == "ACTIVE":
                    conn.compute.stop_server(server)

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
            self.server: Server = conn.compute.get_server(self.server)
            if (
                self.server.status != "SHUTOFF"
                or self.server.task_state != "shutting-off"
                or self.server.task_state is None
            ):
                print(self.server.task_state)
                self.server.stop(conn)
            return

    def power_on(self):
        with openstack.connect(self.cloud) as conn:
            self.server: Server = conn.compute.get_server(self.server)
            if (
                self.server.status != "ACTIVE"
                or self.server.task_state != "powering-on"
                or self.server.task_state is None
            ):
                print(self.server.task_state)
                self.server.start(conn)
            return

    def power_reset(self):
        with openstack.connect(self.cloud) as conn:
            conn.compute.reboot_server(self.server, reboot_type="SOFT")

    def power_shutdown(self):
        # Should attempt a clean shutdown
        with openstack.connect(self.cloud) as conn:
            conn.compute.stop_server(self.server)
