from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from virtbmc_core import Bmc

if TYPE_CHECKING:
    from logging import Logger
    from typing import Literal, Optional

    # fmt: off
    status = Literal[
        "ACTIVE", "BUILDING", "DELETED", "ERROR", "HARD_REBOOT", "PASSWORD",
        "PAUSED", "REBOOT", "REBUILD", "RESCUED", "RESIZED", "REVERT_RESIZE",
        "SHUTOFF", "SOFT_DELETED", "STOPPED", "SUSPENDED", "UNKNOWN",
        "VERIFY_RESIZE"]
    # fmt: on

log: Logger = logging.getLogger("virtbmc_openstack")


try:
    import openstack
    import openstack.exceptions

    if TYPE_CHECKING:
        from openstack.compute.v2.server import Server
        from openstack.connection import Connection

except ImportError as e:
    import sys
    import textwrap

    msg: str = f"""{e}
        Missing required dependency 'openstacksdk'.
        Please install it using pip or other preferred method.

            Command to install it using pip:

                $ pip install openstacksdk

        in case of more questions consult upstream documentation: https://docs.openstack.org/openstacksdk/latest/install/index.html\
        """  # TODO: Switch/add virtbmc documentation
    log.critical(textwrap.dedent(msg))
    sys.exit(-1)


# Command failed and can be retried
IPMI_COMMAND_NODE_BUSY = 0xC0
# Command not valid in this state
IPMI_NOT_VALID_IN_THIS_STATE = 0xD5
# Invalid data field in request
IPMI_INVALID_DATA = 0xCC


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

    def start(self) -> None:
        self.conn = openstack.connect(cloud=self.cloud)
        server: Optional[Server] = self.conn.compute.find_server(self.name)
        if server is None:
            log.error(
                f"server: {self.name} not found \
                      in the {self.cloud} cloud, stopping bmc"
            )
            self.stop()
        else:
            self.server = server
            log.info(f"{self.name} started with connection to cloud: {self.cloud}")
            super().listen()

    def stop(self) -> None:
        self._running = False
        log.info(f"{self.name} stopped, closing the connection to the cloud")
        self.conn.close()

    # BMC Operations
    # ref: 28.3 Chassis Control Command: https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-intelligent-platform-mgt-interface-spec-2nd-gen-v2-0-spec-update.pdf
    def cold_reset(self) -> int:
        log.debug("cold_reset: caleld, stopping BMC")
        self.stop()
        return 0

    def _refresh_server_state(self) -> None:
        server = self.conn.compute.get_server(self.server)
        log.debug(
            f"Refreshing server status: current server status: BMC: {self!r}; \
                status: {self.server.status}; vm_state: {self.server.vm_state}; \
                task_state: {self.server.task_state};"
        )
        if self.server is None:
            log.error("server stopped existing in meantime, exiting")
            if self._running:
                self.stop()
        self.server = server

    def is_active(self) -> bool:
        log.debug("is_active: called")
        self._refresh_server_state()
        return self.server.status != "SHUTOFF"

    def get_power_state(self) -> Literal["on", "off"]:
        log.debug("get_power_state: called")
        return "on" if self.is_active() else "off"

    def power_off(self) -> int:
        log.debug("power_off: called")
        self._refresh_server_state()
        if (
            self.server.status == "SHUTOFF" and self.server.task_state != "powering-on"
        ) or self.server.task_state == "powering-off":
            return 0
        if self.server.task_state:
            return IPMI_COMMAND_NODE_BUSY
        if self.server.status == "ACTIVE":
            self.server.stop(self.conn.compute)
            return 0

        return IPMI_COMMAND_NODE_BUSY

    def power_on(self, refresh: bool = True) -> int:
        log.debug("power_on: called")

        if refresh:
            self._refresh_server_state()

        if self.server.status != "SHUTOFF" or self.server.task_state == "powering-on":
            return 0

        if self.server.task_state:
            return IPMI_COMMAND_NODE_BUSY

        if self.server.status in ["SHUTOFF", "STOPPED"]:
            self.server.start(self.conn.compute)
            return 0

        return IPMI_COMMAND_NODE_BUSY

    def power_reset(self) -> int:
        log.debug("power_reset: called")
        self._refresh_server_state()
        if self.server.status == "REBOOT":
            return 0
        if self.server.task_state:
            return IPMI_COMMAND_NODE_BUSY
        if self.server.status in ["SHUTOFF", "STOPPED"]:
            self.power_on(refresh=False)
        if self.server.status == "ACTIVE":
            self.server.reboot(self.conn.compute, reboot_type="SOFT")
            return 0

        return IPMI_COMMAND_NODE_BUSY

    def power_cycle(self) -> int:
        log.debug("power_cycle: called")
        self._refresh_server_state()
        if self.server.status == "HARD_REBOOT":
            return 0
        if self.server.task_state:
            return IPMI_COMMAND_NODE_BUSY
        if self.server.status in ["SHUTOFF", "STOPPED"]:
            self.power_on(refresh=False)
        if self.server.status == "ACTIVE":
            self.server.reboot(self.conn.compute, reboot_type="HARD")
            return 0

        return IPMI_COMMAND_NODE_BUSY

    def power_shutdown(self) -> int:
        # Should attempt a clean shutdown but openstack doesn't know the difference
        log.debug("power_shutdown: called")
        self.power_off()
        return 0
