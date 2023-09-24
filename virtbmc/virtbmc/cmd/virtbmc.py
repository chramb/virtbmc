from __future__ import annotations

import logging
import os
from argparse import ArgumentParser, HelpFormatter
from importlib.metadata import version
from typing import TYPE_CHECKING

from virtbmc.api.rpc.client import Client
from virtbmc.driver import driver
from virtbmc_core.log import log_format

if TYPE_CHECKING:
    from argparse import Action, Namespace
    from typing import Optional, Sequence


log = logging.getLogger("osbmc")
log_format(log)


def name_arg(parser: ArgumentParser) -> Action:
    return parser.add_argument("name", action="store", help="Name of managed instance")


def names_arg(parser: ArgumentParser) -> Action:
    return parser.add_argument(
        "names", nargs="+", help="A list of managed instances names"
    )


driver_name = os.environ.get("VIRTBMC_DRIVER", "openstack")


def cli(args: Optional[Sequence[str]] = None) -> Namespace:
    # fmt: off
    parser = ArgumentParser(prog="virtbmc", add_help=False)
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")  # noqa: E501
    parser.add_argument("-V","--version", action="version",version=version("virtbmc"), help="Show program's version number and exit")  # noqa: E501
    parser.add_argument("-d","--debug", action="store_true", help="Enable logging debug information to console")  # noqa: E501
    # parser.add_argument("--driver", action="store", default="dummy", help="BMC driver to use (default: 'dummy')")  # noqa: E501

    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # Add Command
    add_parser = subparsers.add_parser("add", help="Create a new virtual BMC for a managed instance", formatter_class=lambda prog: HelpFormatter(prog, max_help_position=40))  # noqa: E501
    driver[driver_name].cli(add_parser) # TODO: figure out how to add to help
    # Delete Command
    delete_parser = subparsers.add_parser("delete", help="Delete a virtual BMC for a managed instance")  # noqa: E501
    names_arg(delete_parser)

    # Start Command
    start_parser = subparsers.add_parser("start", help="Start a virtual BMC for a managed instance")  # noqa: E501
    names_arg(start_parser)

    # Stop Command
    stop_parser = subparsers.add_parser("stop", help="Stop a virtual BMC for a managed instance")  # noqa: E501
    names_arg(stop_parser)

    # List Command
    subparsers.add_parser("list", help="List all virtual BMCs")

    # Show Command
    show_parser = subparsers.add_parser("show", help="Show virtual BMC properties")
    name_arg(show_parser)

    # fmt: on
    return parser.parse_args(args=args)


def main(args: Optional[Sequence[str]] = None) -> int:
    namespace = cli(args)
    client = Client(address="/tmp/virtbmc.sock", authkey=b"pass")
    client.connect()
    if namespace.command == "add":
        print("running add")
        client.bmc_create(driver[driver_name].from_namespace(namespace).config())
    if namespace.command == "delete":
        for name in namespace.names:
            client.bmc_delete(name)
    if namespace.command == "start":
        for name in namespace.names:
            client.bmc_start(name)
    if namespace.command == "stop":
        for name in namespace.names:
            client.bmc_stop(name)
    if namespace.command == "list":
        print(client.bmc_get_all())
    if namespace.command == "show":
        print(client.bmc_get(namespace.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
