from __future__ import annotations

import importlib.metadata
import logging
import sys
from argparse import ArgumentParser, HelpFormatter
from typing import TYPE_CHECKING

import keystoneauth1.exceptions.auth_plugins
import keystoneauth1.exceptions.base
import openstack

from virtbmc.driver.openstack._bmc import OpenStackBMC
from virtbmc.log import log_format

if TYPE_CHECKING:
    from argparse import Namespace
    from typing import Sequence


def main(args: Sequence[str] = sys.argv) -> int:
    log: logging.Logger = logging.getLogger("virtbmc.driver.openstack")
    log_format(logger=log)
    # fmt: off
    prog = "python -m virtbmc.driver.openstack"
    parser = ArgumentParser(prog=prog, add_help=False, formatter_class=lambda prog: HelpFormatter(prog, max_help_position=36))  # noqa: E501
    group = parser.add_argument_group("VirtBMC Options")
    group.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    group.add_argument("-V","--version", action="version",version=importlib.metadata.version("virtbmc"), help="Show program's version number and exit")  # noqa: E501
    group.add_argument("-d","--debug", action="store_true", help="Enable logging debug information to console")
    group.add_argument("--os-debug", action="store_true", help="Enable logging debug information for openstacksdk")
    group.add_argument("server", action="store", help="Name or uuid of managed server")  # fmt: skip
    # fmt: on

    try:
        _ = openstack.connect(options=parser)  # type: ignore
    except keystoneauth1.exceptions.base.ClientException as e:
        known, _ = parser.parse_known_args(args[1:])
        log.critical(e, exc_info=known.debug)

        if isinstance(e, keystoneauth1.exceptions.auth_plugins.MissingRequiredOptions):  # noqa: SIM102
            if len(e.options) == 1 and e.options[0].name == "auth-url":  # type: ignore
                log.error("Missing auth_url did you forget to specify 'OS_CLOUD'?")

        return -1

    parsed: Namespace = parser.parse_args(args=args[1:] if args else None)

    if parsed.os_debug:
        openstack.enable_logging(debug=True)

    if parsed.debug:
        log.setLevel(logging.DEBUG)
        log.debug("Enabled debugging from cli")

    if parsed.server is None:
        parser.print_usage()
        return -1

    bmc = None
    try:
        bmc = OpenStackBMC(**vars(parsed), cloud=parsed.os_cloud, _log=log)
        bmc.start()

    except KeyboardInterrupt:
        if bmc:
            bmc.stop()

        log.info("Interrupt received. Exiting.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
