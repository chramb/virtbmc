from __future__ import annotations

import importlib.metadata
import logging
from argparse import ArgumentParser, HelpFormatter
from typing import TYPE_CHECKING

import openstack

from virtbmc_core.cli import bmc_options
from virtbmc_core.log import log_format
from virtbmc_openstack import OpenStackBMC

if TYPE_CHECKING:
    from argparse import Namespace
    from typing import Optional, Sequence

log: logging.Logger = logging.getLogger("virtbmc_openstack")


def main(args: Optional[Sequence[str]] = None) -> int:
    # fmt: off
    parser = ArgumentParser(prog="python -m virtbmc_openstack", add_help=False, formatter_class=lambda prog: HelpFormatter(prog, max_help_position=36))  # noqa: E501
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")  # noqa: E501
    parser.add_argument("-V","--version", action="version",version=importlib.metadata.version(__package__), help="Show program's version number and exit")  # noqa: E501
    parser.add_argument("-d","--debug", action="store_true", help="enable logging debug information to console")  # noqa: E501

    parser, group = bmc_options(parser)
    group.add_argument("--mode", action="store", default="safe", choices=("safe", "unsafe", "cached", "simple"), help="Chose api communication strategy")  # noqa: E501
    group.add_argument("server", action="store", help="Name or uuid of managed server")  # noqa: E501
    # fmt: on

    _ = openstack.connect(options=parser)  # type: ignore
    parsed: Namespace = parser.parse_args(args=args)
    log_format(log)

    if parsed.debug:
        log.setLevel(logging.DEBUG)
        log.debug("Enabled debugging from cli")
    bmc = None
    try:
        bmc = OpenStackBMC(
            name=parsed.server,
            mode=parsed.mode,
            address=parsed.address,
            port=parsed.port,
            username=parsed.username,
            password=parsed.password,
            cloud=parsed.os_cloud,
        )
        bmc.start()

    except KeyboardInterrupt:
        if bmc:
            bmc.stop()
        print("Interrupt received. Exiting.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
