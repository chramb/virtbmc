from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

import openstack
import openstack.exceptions

from virtbmc.core import Bmc
from virtbmc.core.constants import IPMI_COMPLETION_CODES as CODE

if TYPE_CHECKING:
    from typing import Literal, Sequence, Union

    from openstack.compute.v2.server import Server
    from openstack.connection import Connection

    from virtbmc.core.types import BmcConfig, ipmi_boot_device
    from virtbmc.driver.openstack.types import task_state, vm_state

    error_vm_states = Union[task_state, vm_state]


class OpenStackBMC(Bmc):
    driver: str = "openstack"

    def __init__(self, **kwargs: Unpack[BmcConfig]) -> None:
        super().__init__(**{k: v for k, v in kwargs.items() if v is not None})
        self._server: Server
        self._conn: Connection

        if (cloud := self.properties.get("openstack_cloud")) is None:
            msg = "missing required property 'openstack_cloud'"
            raise TypeError(msg)

        self.cloud = cloud

    def start(self, timeout: int = 30) -> None:
        # TODO: add timeout when connecting for too long
        self._conn = openstack.connect(cloud=self.cloud)
        server: Server | None = self._conn.compute.find_server(self.name)
        if server is not None:
            self._server = server

            self.log.info(f"{self.name} started and connected to the cloud")
            super().start(timeout=timeout)

        else:
            self.log.error(f"server: {self.name} not found in the cloud, stopping bmc")  # fmt: skip
            self.stop()

    def stop(self) -> None:
        self._conn.close()
        super().stop()

    def _handle_nova_exception(
        self,
        exception: openstack.exceptions.ConflictException,
        desired_states: Sequence[error_vm_states],
    ) -> CODE:
        if exception.details is not None:
            received_state: error_vm_states | str = exception.details.split(" ")[-1]

            if received_state in desired_states:
                return CODE.SUCCESS

        self.log.error(f"Recived exception outside of 'desired_states': {exception}")
        return CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE

    # BMC Operations
    # ref: 28.3 Chassis Control Command: https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-intelligent-platform-mgt-interface-spec-2nd-gen-v2-0-spec-update.pdf
    def is_active(self) -> bool:
        server = self._conn.compute.get_server(self._server)

        if self._server is None:
            self.log.error("Server stopped existing in meantime, stopping the bmc")

            if not self._stopped:
                self.stop()

            return False

        self.log.debug(
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
        self.stop()
        return CODE.SUCCESS

    def get_power_state(self) -> Literal["on", "off"]:
        return "on" if self.is_active() else "off"

    def power_off(self) -> CODE:
        try:
            self._server.stop(self._conn.compute)
            return CODE.SUCCESS

        except openstack.exceptions.ConflictException as e:
            return self._handle_nova_exception(e, ("powering-off", "stopped"))

    def power_on(self) -> CODE:
        try:
            self._server.start(self._conn.compute)
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException as e:
            return self._handle_nova_exception(e, ("active", "powering-on"))

    def power_reset(self) -> CODE:
        try:
            self._server.reboot(self._conn.compute, "SOFT")
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException as e:
            _states = ("reboot_pending", "reboot_started", "rebooting")
            return self._handle_nova_exception(e, _states)

    def power_cycle(self) -> CODE:
        try:
            self._server.reboot(self._conn.compute, "HARD")
            return CODE.SUCCESS
        except openstack.exceptions.ConflictException as e:
            _states = ("reboot_pending_hard", "reboot_started_hard", "rebooting_hard")
            return self._handle_nova_exception(e, _states)

    def power_shutdown(self) -> CODE:
        return self.power_off()

    def get_boot_device(self) -> ipmi_boot_device:
        try:
            pxe_first = self._server.get_metadata_item(self._conn.compute, "libvirt:pxe-first").metadata.get(
                "libvirt:pxe-first", ""
            )  # type: ignore
        except openstack.exceptions.ResourceNotFound:
            pxe_first = ""

        return "network" if pxe_first == "1" else "hd"

    def set_boot_device(self, bootdevice: ipmi_boot_device) -> None:
        if bootdevice == "hd":
            self._server.set_metadata_item(self._conn.compute, "libvirt:pxe-first", "")
        elif bootdevice in ("network", "net", "pxe"):
            self._server.set_metadata_item(self._conn.compute, "libvirt:pxe-first", "1")
        else:
            self.log.error(f"unsupported boot device: {bootdevice}, skipping command")
