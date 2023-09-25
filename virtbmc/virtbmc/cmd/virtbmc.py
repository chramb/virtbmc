from __future__ import annotations

import logging
import os
from argparse import ArgumentParser, HelpFormatter
from importlib.metadata import version
from multiprocessing.managers import RemoteError
from pathlib import Path
from typing import TYPE_CHECKING

from prettytable import SINGLE_BORDER, PrettyTable

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
    sock = "/tmp/virtbmc.sock"
    namespace = cli(args)
    client = Client(address=sock, authkey=b"pass")
    if not Path(sock).exists():
        print(f"Error: missing {sock}. Is the daemon running?")
        return -1

    client.connect()
    try:
        if namespace.command == "add":
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
            if bmcs := client.bmc_get_all():
                # fmt: off
                table = PrettyTable(
                    field_names=(
                        "NAME", "ACTIVE", "ADDRESS", "PORT",
                        "USERNAME", "PASSWORD", "DRIVER",))
                table.add_rows(
                    ( bmc.get("driver"), bmc.get("active"), bmc.get("address"),
                     bmc.get("port"), bmc.get("username"), bmc.get("password"),
                     bmc.get("name"),)
                    for bmc in bmcs)
                # fmt: on
                table.set_style(style=SINGLE_BORDER)
                print(table)
            else:
                print("Error: No BMCs currently created")
                return -1
        if namespace.command == "show":
            if bmc := client.bmc_get(namespace.name):
                table = PrettyTable(field_names=("Property", "Value"))
                table.add_rows((k, v) for k, v in bmc.items())
                table.set_style(SINGLE_BORDER)
                print(table)
            else:
                print("Error: bmc with that name doesn't exist")
                return -1
    except RemoteError as e:
        # Hack to get error msg for now
        print("Error:" + e.args[-1].split(":")[-1][:-1])
        return -1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
