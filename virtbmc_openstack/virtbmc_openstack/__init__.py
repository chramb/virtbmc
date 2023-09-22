from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import openstack
import openstack.exceptions

from virtbmc_core import Bmc
from virtbmc_core.constants import IPMI_COMPLETION_CODES as CODE

if TYPE_CHECKING:
    from argparse import Namespace
    from logging import Logger
    from typing import Literal, Optional, Sequence, Union

    from openstack.compute.v2.server import Server
    from openstack.connection import Connection

    from virtbmc_core.bmc import ActionsContainer
    from virtbmc_openstack.types import task_state, vm_state

    error_vm_states = Union[task_state, vm_state]

log: Logger = logging.getLogger("virtbmc.driver.openstack")


def handle_nova_exception(
    exception: openstack.exceptions.ConflictException,
    desired_states: Sequence[error_vm_states],
) -> CODE:
    if exception.details is not None:
        received_state: Union[error_vm_states, str] = exception.details.split(" ")[-1]

        if received_state in desired_states:
            return CODE.SUCCESS

    log.error(f"Recived exception outside of 'desired_states': {exception}")
    return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE


class OpenStackBMC(Bmc):
    driver: str = "openstack"

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
        self._server: Server
        self._conn: Connection
        self.name = name
        self.cloud = cloud

    def start(self, timeout: int = 30) -> None:
        # TODO: add timeout when connecting for too long

        self._conn = openstack.connect(cloud=self.cloud)
        server: Optional[Server] = self._conn.compute.find_server(self.name)

        if server is not None:
            self._server = server

            log.info(f"{self.name} started with connection to cloud")
            super().start(timeout=timeout)

        else:
            log.error(f"server: {self.name} not found in the cloud, stopping bmc")
            self.stop()

    def stop(self) -> None:
        self._conn.close()
        super().stop()

    @staticmethod
    def cli(parser: ActionsContainer, os_cloud: bool = True) -> ActionsContainer:
        # fmt: off
        if os_cloud:
            parser.add_argument("--os-cloud", metavar="NAME", help="Named cloud to connect to")  # noqa: E501
        parser.add_argument("server", action="store", help="Name or uuid of managed server")  # noqa: E501
        # fmt: on
        return Bmc.cli(parser)

    @staticmethod
    def from_namespace(namespace: Namespace) -> OpenStackBMC:
        return OpenStackBMC(
            name=namespace.server,
            address=namespace.address,
            port=namespace.port,
            username=namespace.username,
            password=namespace.password,
            cloud=namespace.os_cloud,
        )

    # BMC Operations
    # ref: 28.3 Chassis Control Command: https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-intelligent-platform-mgt-interface-spec-2nd-gen-v2-0-spec-update.pdf
    def is_active(self) -> bool:
        server = self._conn.compute.get_server(self._server)

        if self._server is None:
            log.error("Server stopped existing in meantime, stopping the bmc")

            if not self._stopped:
                self.stop()

            return False

        log.debug(
            "Refreshed server status: current server "
            f"status: {self._server.status}; "
            f"vm_state: {self._server.vm_state}; "
            f"task_state: {self._server.task_state};"
        )

        self._server = server
        return (
            self._server.status == "ACTIVE"
            and self._server.task_state is None
            or self._server.status == "SHUTOFF"
            and self._server.task_state == "powering-on"
        )

    def cold_reset(self) -> CODE:
        log.debug("cold_reset: called, stopping BMC")
        self.stop()
        return CODE.SUCCESS

    def get_power_state(self) -> Literal["on", "off"]:
        log.debug("get_power_state: called")
        return "on" if self.is_active() else "off"

    def power_off(self) -> CODE:
        try:
            self._server.stop(self._conn.compute)
            return CODE.SUCCESS

        except openstack.exceptions.ConflictException as e:
            return handle_nova_exception(e, ("powering-off", "stopped"))

    def power_on(self) -> CODE:
        try:
            self._server.start(self._conn.compute)
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException as e:
            return handle_nova_exception(e, ("active", "powering-on"))

    def power_reset(self) -> CODE:
        try:
            self._server.reboot(self._conn.compute, "SOFT")
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException as e:
            return handle_nova_exception(
                e, ("reboot_pending", "reboot_started", "rebooting")
            )

    def power_cycle(self) -> CODE:
        try:
            self._server.reboot(self._conn.compute, "HARD")
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException as e:
            return handle_nova_exception(
                e, ("reboot_pending_hard", "reboot_started_hard", "rebooting_hard")
            )

    def power_shutdown(self) -> int:
        return self.power_off()
