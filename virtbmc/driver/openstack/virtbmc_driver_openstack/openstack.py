from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Sequence

if TYPE_CHECKING:
    from logging import Logger
    from typing import Dict, Literal, Union

    # fmt: off
    status = Literal[
        "ACTIVE", "BUILDING", "DELETED", "ERROR", "HARD_REBOOT", "PASSWORD", 
        "PAUSED", "REBOOT", "REBUILD", "RESCUED", "RESIZED", "REVERT_RESIZE", 
        "SHUTOFF", "SOFT_DELETED", "STOPPED", "SUSPENDED", "UNKNOWN", 
        "VERIFY_RESIZE"]
    # fmt: on

log: Logger = logging.getLogger("virtbmc.driver.openstack")


try:
    import openstack
    import openstack.exceptions

    if TYPE_CHECKING:
        from openstack.compute.v2.server import Server
        from openstack.connection import Connection

except ImportError as e:
    import sys
    import textwrap

    msg = f"""\
        {e}
        Missing required dependency 'openstacksdk'.
        Please install it using pip or other preferred method.

            Command to install it using pip:

                $ pip install openstacksdk

        in case of more questions consult upstream documentation: https://docs.openstack.org/openstacksdk/latest/install/index.html\
        """  # Switch/add virtbmc documentation if it ever gets created
    log.critical(textwrap.dedent(msg))
    if __name__ == "__main__":
        sys.exit(-1)
    else:
        raise ImportError

from virtbmc_driver_core import BMC

# Command failed and can be retried
IPMI_COMMAND_NODE_BUSY = 0xC0
# Invalid data field in request
IPMI_INVALID_DATA = 0xCC


@dataclass
class OpenStackBMC(BMC):
    name: str
    cloud: Optional[str] = None
    driver: str = field(default="openstack", init=False)
    server: Server = field(init=False, repr=False)
    conn: Connection = field(init=False, repr=False)

    def __post_init__(self) -> None:
        log.debug(f"{self.name} Created")
        return super().__post_init__()

    def listen(self):
        self.conn = openstack.connect(cloud=self.cloud)
        server: Union[Server, None] = self.conn.compute.find_server(self.name)
        if server is None:
            raise Exception(f"Server with name {self.name} not found")
        self.server = server
        log.info(f"{self.name} Started with connection to cloud: {self.cloud}")
        super().listen()

    def stop(self):
        self._started = False
        log.info(f"{self.name} stopped, closing connection to the cloud")
        self.conn.close()

    # BMC Operations
    # ref: 28.3 Chassis Control Command: https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-intelligent-platform-mgt-interface-spec-2nd-gen-v2-0-spec-update.pdf
    def cold_reset(self):
        log.debug("cold_reset: stopping BMC")
        self.stop()
        return 0

    def _refresh_server_state(self):
        server = self.conn.compute.get_server(self.server)
        log.debug(
            f"Refreshing server status: current server status: BMC: {repr(self)}; status: {self.server.status}; vm_state: {self.server.vm_state}; task_state: {self.server.task_state};"
        )
        if self.server is None:
            raise Exception("server stopped existing in meantime")
        # TODO: catch this exception in listen()
        self.server = server

    def is_active(self):
        log.debug("is_active(): called")
        self._refresh_server_state()
        return self.server.status != "SHUTOFF"

    def get_power_state(self):
        log.debug("get_power_state(): called")
        #     "off": 0,
        #     "on": 1,
        return "on" if self.is_active() else "off"

    def power_off(self):
        log.debug("power_off(): called")
        self._refresh_server_state()
        if (
            self.server.status == "SHUTOFF" and self.server.task_state != "powering-on"
        ) or self.server.task_state == "powering-off":
            return
        if self.server.task_state:
            return IPMI_COMMAND_NODE_BUSY
        if self.server.status == "ACTIVE":
            self.server.stop(self.conn.compute)
            return

        return IPMI_COMMAND_NODE_BUSY  # Gets there when rebooting

    def power_on(self, refresh: bool = True):
        log.debug("power_on(): called")
        if refresh:
            self._refresh_server_state()
        if self.server.status != "SHUTOFF" or self.server.task_state == "powering-on":
            return
        if self.server.task_state:
            return IPMI_COMMAND_NODE_BUSY
        if self.server.status in ["SHUTOFF", "STOPPED"]:
            self.server.start(self.conn.compute)
            return

        return IPMI_COMMAND_NODE_BUSY  # Gets there when rebooting

    def power_reset(self):
        log.debug("power_reset: called")
        self._refresh_server_state()
        if self.server.status == "REBOOT":
            return
        if self.server.task_state:
            return IPMI_COMMAND_NODE_BUSY
        if self.server.status in ["SHUTOFF", "STOPPED"]:
            self.power_on(refresh=False)
        if self.server.status == "ACTIVE":
            self.server.reboot(self.conn.compute, reboot_type="SOFT")
            return

        return IPMI_COMMAND_NODE_BUSY  # Unsupported state

    def power_cycle(self):
        log.debug("power_cycle(): called")
        self._refresh_server_state()
        if self.server.status == "HARD_REBOOT":
            return
        if self.server.task_state:
            return IPMI_COMMAND_NODE_BUSY
        if self.server.status in ["SHUTOFF", "STOPPED"]:
            self.power_on(refresh=False)
        if self.server.status == "ACTIVE":
            self.server.reboot(self.conn.compute, reboot_type="HARD")
            return

        return IPMI_COMMAND_NODE_BUSY  # Gets there unsupported state

    def power_shutdown(self):
        # Should attempt a clean shutdown but openstack doesn't know the difference I think
        log.debug("power_shutdown(): called")
        self.power_off()


# TODO: somehow better pass prog
def main(
    args: Optional[Sequence[str]] = None, *, prog="python -m virtbmc.driver.openstack"
) -> int:
    import importlib.metadata
    from argparse import ArgumentParser, HelpFormatter

    # fmt: off
    parser = ArgumentParser(prog=prog, add_help=False, formatter_class=lambda prog: HelpFormatter(prog, max_help_position=36))  # noqa: E501

    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument("-V","--version", action="version",version=importlib.metadata.version("virtbmc"), help="Show program's version number and exit")  # noqa: E501
    parser.add_argument("-d","--debug", action="store_true", help="enable logging debug information to console")

    group = parser.add_argument_group("VirtBMC Options")
    group.add_argument("-u","--username", default="admin", type=str, action="store", help="The BMC username (default: admin)")  # noqa: E501
    group.add_argument("-P","--password", default="password", type=str, action="store", help="The BMC password (default: password)")  # noqa: E501
    group.add_argument("-p","--port", default=623, type=int, action="store", help="Port to listen on (default: 623)")  # noqa: E501
    group.add_argument("-a","--address", default="::", type=str, action="store", help="Address to listen on (default: '::')")  # noqa: E501
    group.add_argument("name", type=str, action="store", help="name or uuid of managed server")
    # fmt: on

    conn = openstack.connect(options=parser)  # type: ignore
    parsed = parser.parse_args()

    if parsed.debug:
        logging.getLogger("virtbmc.driver.openstack").setLevel(logging.DEBUG)
        log.debug("Enabled debugging from cli")
    try:
        bmc = OpenStackBMC(name=parsed.name, cloud=parsed.os_cloud)
        bmc.listen()
    except KeyboardInterrupt:
        log.info("Interrupt received. Exiting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
