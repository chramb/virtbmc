from __future__ import annotations

"""
    def _ensure_status(self, target_status: status, interval: float = 5) -> None:
        # TODO: somehow handle both active and shutoff if changed meant to run in background
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
    def power_off(self):
        try:
            if (
                self.server.vm_state == "stopped"
                or self.server.task_state == "powering-off"
            ):
                return
            if self.server.task_state is None:
                self.server.stop(self.conn)
                self.server.task_state = "powering-off"

            return 0xC1
"""
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

import openstack
import openstack.exceptions
from openstack.compute.v2.server import Server
from openstack.connection import Connection
from requests import session
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

# Command failed and can be retried
IPMI_COMMAND_NODE_BUSY = 0xC0
# Invalid data field in request
IPMI_INVALID_DATA = 0xCC


@dataclass
class OpenStackBMC(BaseBMC):
    name: str
    cloud: Optional[str] = None
    driver: str = field(default="openstack", init=False)
    server: Server = field(init=False, repr=False)
    conn: Connection = field(init=False, repr=False)

    def __post_init__(self) -> None:
        return super().__post_init__()

    def start(self):
        self.conn = openstack.connect(cloud=self.cloud)
        server: Union[Server, None] = self.conn.compute.find_server(self.name)
        if server is None:
            raise Exception(f"Server with name {self.name} not found")
        self.server = server
        print("started")
        super().start()

    def stop(self):
        self._started = False
        self.conn.close()

    # BMC Operations
    # ref: 28.3 Chassis Control Command: https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-intelligent-platform-mgt-interface-spec-2nd-gen-v2-0-spec-update.pdf
    def cold_reset(self):
        self.stop()
        return 0

    def is_active(self):
        print("is active called")
        self.server = self.conn.compute.get_server(self.server)
        if self.server is None:
            raise Exception("server stopped existing in meantime")
        return self.server.status == "ACTIVE"

    def get_power_state(self):
        print("Get power state called")
        #     "off": 0,
        #     "on": 1,
        return "on" if self.is_active() else "off"

    def power_off(self):
        print("called power-off")
        # this should be power down without waiting for clean shutdown
        if self.server.status == "SHUTOFF" or self.server.task_state == "powering-off":
            return

        # try:
        if self.is_active():
            self.server.stop(self.conn.compute)
            self.server.task_state = "powering-off"
            self.server.vm_state = "stopped"
            return
        # except openstack.exceptions.ConflictException:
        #     pass
        self.server = self.conn.compute.get_server(self.server)
        return IPMI_COMMAND_NODE_BUSY  # Gets there when rebooting

    def power_on(self, task_state: str = "powering-on"):
        print("called power on")
        if self.server.status == "ACTIVE" or self.server.task_state == "powering-on":
            return

        if self.server.status in ["SHUTOFF", "STOPPED"]:
            self.server.start(self.conn.compute)
            self.server.task_state = task_state
            self.server.vm_state = "active"
            return

        self.server = self.conn.compute.get_server(self.server)
        return IPMI_COMMAND_NODE_BUSY  # Gets there when rebooting

    def power_reset(self):
        print("reset called")
        if self.server.task_state in ["rebooting", "reboot_started"]:
            return
        if self.server.vm_state == "stopped":
            self.power_on(task_state="rebooting")
        if self.is_active():  # if self.server.task_state in ["ACTIVE", "SHUTOFF"]:
            self.server.reboot(self.conn.compute, reboot_type="SOFT")
            self.server.task_state = "rebooting"
            return
        else:
            self.power_on(task_state="rebooting")
            return

    def power_cycle(self):
        print("cycle called")
        if self.server.task_state in ["rebooting_hard", "reboot_started_hard"]:
            return
        # if self.server.vm_state == "stopped":
        if self.is_active():  # if self.server.task_state in ["ACTIVE", "SHUTOFF"]:
            self.server.reboot(self.conn.compute, reboot_type="HARD")
            self.server.task_state = "rebooting_hard"
            return
        else:
            self.power_on(task_state="rebooting_hard")
            return

    def power_shutdown(self):
        print("called shutdown")
        # Should attempt a clean shutdown but openstack doesn't know the difference I think
        self.power_off()
