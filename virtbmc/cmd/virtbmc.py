# ruff: noqa: E402
from __future__ import annotations

import importlib.metadata
import logging
import os
from argparse import ArgumentParser, HelpFormatter
from pathlib import Path
from typing import TYPE_CHECKING, Any

from prettytable import SINGLE_BORDER, PrettyTable

log = logging.getLogger("virtbmc")

from virtbmc.log import log_format

log_format(log)

DEBUG = os.environ.get("VIRTBMC_DEBUG", False)
if DEBUG:
    log.setLevel(logging.DEBUG)

from virtbmc.config import CONFIG_LOCATION, get_config_value

if get_config_value("virtbmc.debug") is True:
    log.setLevel(logging.DEBUG)

from virtbmc.api import client
from virtbmc.config import DEFAULT_CONFIG, get_config_value

if TYPE_CHECKING:
    from argparse import Action
    from typing import Sequence


def name_arg(parser: ArgumentParser) -> Action:
    return parser.add_argument("name", help="Name of BMC")  # fmt: skip


def names_arg(parser: ArgumentParser) -> Action:
    return parser.add_argument("name", nargs="+", help="A list of names of BMCs")  # fmt: skip


# fmt: off
def cli() -> ArgumentParser:
    parser = ArgumentParser(prog="virtbmc", add_help=False, formatter_class=lambda prog: HelpFormatter(prog, max_help_position=30))  # noqa: E501
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument("-V", "--version", action="version",version=importlib.metadata.version("virtbmc"), help="Show program's version number and exit")  # noqa: E501
    _CONFIG_LOCATION=os.environ.get("VIRTBMC_CONFIG", CONFIG_LOCATION)
    parser.add_argument("-f", "--config", action="store", default=_CONFIG_LOCATION, type=Path, help=f"Config file location (default: {_CONFIG_LOCATION})")  # noqa: E501
    _HOST=os.environ.get("VIRTBMC_HOST", get_config_value("virtbmc.host", DEFAULT_CONFIG))
    parser.add_argument("-H", "--host", action="store", default=_HOST, help=f"daemon socket to connect to (default: {_HOST})")  # noqa: E501
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    _ = subparsers.add_parser("info", help="Display information and exit")

    # Start Command
    start_parser = subparsers.add_parser("start", help="Start a virtual BMC for a managed instance")
    name_arg(start_parser)

    # Stop Command
    stop_parser = subparsers.add_parser("stop", help="Stop a virtual BMC for a managed instance")
    name_arg(stop_parser)

    # List Command
    list_parser = subparsers.add_parser("list", help="List all virtual BMCs")
    list_parser.add_argument("--only-active", action="store_true" ,help="List only active BMCs")

    # Show Command
    show_parser = subparsers.add_parser("show", help="Show virtual BMC properties")
    name_arg(show_parser)

    # Create Command
    create_parser = subparsers.add_parser("create", help="Create a new virtual BMC for a managed instance", formatter_class=lambda prog: HelpFormatter(prog, max_help_position=40), add_help=True)  # noqa: E501
    create_parser.add_argument("-d","--driver", required=True, type=str, action="store", help="VirtBMC Driver to use (default: None)")  # noqa: E501
    create_parser.add_argument("-n","--name", required=True, type=str, action="store", help="Name to reference BMC by (default: None)")  # noqa: E501
    create_parser.add_argument("-u","--username", default=get_config_value("bmc.username"), type=str, action="store", help="The BMC username (default: admin)") # noqa: E501
    create_parser.add_argument("-P","--password", default=get_config_value("bmc.password"), type=str, action="store", help="The BMC password (default: password)") # noqa: E501
    create_parser.add_argument("-p","--port", default=get_config_value("bmc.port"), type=int, action="store", help="Port to listen on (default: 623)") # noqa: E501
    create_parser.add_argument("-a","--address", default=get_config_value("bmc.address"), type=str, action="store", help="Address to listen on (default: '::')") # noqa: E501
    create_parser.add_argument("--property", default=[], type=str, action="append", metavar="KEY=VALUE", help="Additional properties") # noqa: E501

    # Delete Command
    delete_parser = subparsers.add_parser("delete", help="Delete a virtual BMC for a managed instance")
    name_arg(delete_parser)

    return parser
# fmt: on


def main(argv: Sequence[str] | None = None) -> int:
    parser = cli()
    ns = parser.parse_args(argv)
    command: str | None = getattr(ns, "command")

    if command is None:
        parser.print_help()
        return -1

    try:
        if command == "create":
            properties: dict[str, Any] = get_config_value("bmc.properties")
            for prop in ns.property:
                k, v = prop.split("=")
                properties[k] = v

            client.create(
                driver=ns.driver,
                name=ns.name,
                address=ns.address,
                port=ns.port,
                username=ns.username,
                password=ns.password,
                properties=properties,
            )

        if command == "delete":
            client.delete(ns.name)
        if command == "start":
            client.start(ns.name)
        if command == "stop":
            client.stop(ns.name)

        if command == "list":
            result = client.list(ns.only_active)
            if len(result) == 0:
                return 0
            table = PrettyTable(field_names=result[0].keys())  # TODO :organize and capitalize
            table.set_style(SINGLE_BORDER)  # type: ignore
            for bmc in result:
                table.add_row(bmc.values())  # type: ignore
            print(table)
        if command == "show":
            result = client.show(ns.name)
            if result is None:
                return 0
            table = PrettyTable(field_names=("Key", "Value"))
            table.align = "l"
            table.set_style(SINGLE_BORDER)  # type: ignore
            table.add_rows(  # type: ignore
                (
                    ("Name", result["name"]),
                    ("Driver", result["driver"]),
                    ("Username", result["username"]),
                    ("Password", result["password"]),
                    ("Address", result["address"]),
                    ("Port", result["port"]),
                    ("Properties", [result["properties"]]),
                )
            )
            print(table)
    except client.VirtBmcApiClientError as e:
        log.error(e.msg)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
