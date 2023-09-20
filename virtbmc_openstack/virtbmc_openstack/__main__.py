from __future__ import annotations

import importlib.metadata
import logging
from argparse import ArgumentParser, HelpFormatter
from typing import TYPE_CHECKING

import openstack

from virtbmc_core.log import log_format
from virtbmc_openstack import OpenStackBMC

if TYPE_CHECKING:
    from argparse import Namespace
    from typing import Optional, Sequence

log: logging.Logger = logging.getLogger("virtbmc.driver.openstack")


def main(args: Optional[Sequence[str]] = None) -> int:
    # fmt: off
    parser = ArgumentParser(prog="python -m virtbmc_openstack", add_help=False, formatter_class=lambda prog: HelpFormatter(prog, max_help_position=36))  # noqa: E501
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")  # noqa: E501
    parser.add_argument("-V","--version", action="version",version=importlib.metadata.version(__package__), help="Show program's version number and exit")  # noqa: E501
    parser.add_argument("-d","--debug", action="store_true", help="Enable logging debug information to console")  # noqa: E501
    parser.add_argument("--os-debug", action="store_true", help="Enable logging debug information for openstacksdk")  # noqa: E501
    _ = openstack.connect(options=parser)  # type: ignore

    group = parser.add_argument_group("VirtBMC Options")
    group= OpenStackBMC.cli(group, os_cloud=False)
    # fmt: on

    parsed: Namespace = parser.parse_args(args=args)
    log_format(log)

    if parsed.os_debug:
        openstack.enable_logging(debug=True)

    if parsed.debug:
        log.setLevel(logging.DEBUG)
        log.debug("Enabled debugging from cli")

    bmc = None
    try:
        bmc = OpenStackBMC.from_namespace(parsed)
        bmc.start()

    except KeyboardInterrupt:
        if bmc:
            bmc.stop()
        print("Interrupt received. Exiting.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
