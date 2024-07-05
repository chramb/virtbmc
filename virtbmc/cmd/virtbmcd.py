# ruff: noqa: E402
from __future__ import annotations

import importlib.metadata
import logging
import os
import urllib.parse
from argparse import ArgumentParser, HelpFormatter
from pathlib import Path
from typing import TYPE_CHECKING

log = logging.getLogger("virtbmc")

from virtbmc.log import log_format

log_format(log)

DEBUG = os.environ.get("VIRTBMC_DEBUG", False)
if DEBUG:
    log.setLevel(logging.DEBUG)

from virtbmc.config import CONFIG_LOCATION, get_config_value

if get_config_value("virtbmc.debug") is True:
    log.setLevel(logging.DEBUG)

import virtbmc._manager as mgr
from virtbmc.api.server import serve_forever

if TYPE_CHECKING:
    from typing import Sequence


# fmt: off
def cli() -> ArgumentParser:
    parser = ArgumentParser(prog="virtbmc", add_help=False, description="Run VirtBMC Daemon that manages individual Virtual BMCs", formatter_class=lambda prog: HelpFormatter(prog, max_help_position=30))  # noqa: E501  # noqa: E501
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument("-V", "--version", action="version",version=importlib.metadata.version("virtbmc"), help="Show program's version number and exit")  # noqa: E501
    parser.add_argument("-D", "--debug", action="store_true", help="Enable logging debug information")
    _CONFIG_LOCATION=os.environ.get("VIRTBMC_CONFIG",CONFIG_LOCATION)
    parser.add_argument("-f", "--config", action="store", type=Path, help=f"Config file location (default: {_CONFIG_LOCATION})")  # noqa: E501
    _HOST=os.environ.get("VIRTBMC_HOST", get_config_value("virtbmc.host")) # type: ignore
    parser.add_argument("-H", "--host", action="store", default=_HOST, help=f"daemon socket to connect to (default: {_HOST})")  # noqa: E501

    return parser
# fmt: on


def main(argv: Sequence[str] | None = None) -> int:
    parser = cli()
    ns = parser.parse_args(argv)
    _host: str = ns.host
    host: urllib.parse.SplitResult = urllib.parse.urlsplit(_host)

    if ns.debug:
        log.setLevel(logging.DEBUG)
        log.debug("Enabled Debugging through CLI")

    if (p := Path(host.path)).exists():
        msg = (
            "ERROR: virtbmc socket already exists,"
            "this can a happen if virtbmc daemon is already running"
            "or was forcefully closed, if you're sure you want"
            f"to start the daemon please delete: '{host.path}'"
        )
        log.critical((msg))
        return -1

    try:
        log.debug("starting server")
        mgr.init()
        serve_forever(_host, mgr)

    except KeyboardInterrupt:
        try:
            log.info("stopping all Bmcs, press ^C once again to force exit.")
            p.unlink()
            mgr.exit()
        except KeyboardInterrupt:
            log.warning("Force Quitting!")
            p.unlink(True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
