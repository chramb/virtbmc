from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import openstack
import openstack.exceptions

from virtbmc_core import Bmc
from virtbmc_core.constants import IPMI_COMPLETION_CODES as CODE

if TYPE_CHECKING:
    from logging import Logger
    from typing import Literal, Optional, Sequence, Union

    from openstack.compute.v2.server import Server
    from openstack.connection import Connection

    from virtbmc_openstack.types import task_state, vm_state

    error_vm_states = Union[task_state, vm_state]

log: Logger = logging.getLogger(__name__)


def handle_nova_exception(
    exception: openstack.exceptions.ConflictException,
    desired_states: Sequence[error_vm_states],
) -> CODE:
    if exception.details is not None:
        received_state: Union[error_vm_states, str] = exception.details.split(" ")[-1]
        if received_state in desired_states:
            return CODE.SUCCESS

    return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE


class OpenStackBMC(Bmc):
    driver: str = "openstack"
    server: Server
    conn: Connection

    def __init__(
        self,
        name: str,
        cloud: Optional[str] = None,
        username: str = "admin",
        password: str = "password",
        port: int = 623,
        address: str = "::",
    ) -> None:
        super().__init__(username, password, port, address)
        self.name = name
        self.cloud = cloud

    def start(self, timeout: int = 30) -> None:
        # TODO: add timeout when connecting for too long

        self.conn = openstack.connect(cloud=self.cloud)
        server: Optional[Server] = self.conn.compute.find_server(self.name)

        if server is not None:
            self.server = server

            log.info(f"{self.name} started with connection to cloud")
            super().start(timeout=timeout)

        else:
            log.error(f"server: {self.name} not found in the cloud, stopping bmc")
            self.stop()

    def stop(self) -> None:
        self.conn.close()
        super().stop()

    # BMC Operations
    # ref: 28.3 Chassis Control Command: https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-intelligent-platform-mgt-interface-spec-2nd-gen-v2-0-spec-update.pdf
    def is_active(self) -> bool:
        server = self.conn.compute.get_server(self.server)
        log.debug(
            "Refreshed server status: current server "
            f"status: {self.server.status}; "
            f"vm_state: {self.server.vm_state}; "
            f"task_state: {self.server.task_state};"
        )

        if self.server is None:
            log.error("Server stopped existing in meantime, stopping the bmc")

            if not self._stopped:
                self.stop()

        self.server = server
        return self.server.status == "ACTIVE"

    def cold_reset(self) -> CODE:
        log.debug("cold_reset: caleld, stopping BMC")
        self.stop()
        return CODE.SUCCESS

    def get_power_state(self) -> Literal["on", "off"]:
        log.debug("get_power_state: called")
        return "on" if self.is_active() else "off"

    def power_off(self) -> CODE:
        try:
            self.server.stop(self.conn.compute)
            return CODE.SUCCESS

        except openstack.exceptions.ConflictException as e:
            return handle_nova_exception(e, ("powering-off", "stopped"))

    def power_on(self) -> CODE:
        try:
            self.server.start(self.conn.compute)
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException as e:
            return handle_nova_exception(e, ("active", "powering-on"))

    def power_reset(self) -> CODE:
        try:
            self.server.reboot(self.conn.compute, "SOFT")
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException as e:
            return handle_nova_exception(
                e, ("reboot_pending", "reboot_started", "rebooting")
            )

    def power_cycle(self) -> CODE:
        try:
            self.server.reboot(self.conn.compute, "SOFT")
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException as e:
            return handle_nova_exception(
                e, ("reboot_pending_hard", "reboot_started_hard", "rebooting_hard")
            )

    def power_shutdown(self) -> int:
        return self.power_off()
