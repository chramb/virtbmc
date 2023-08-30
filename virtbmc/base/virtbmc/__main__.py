from __future__ import annotations

import argparse
import importlib.metadata
import logging
import sys
from typing import TYPE_CHECKING

from virtbmc.config import CONFIG, read
from virtbmc.manager import bmc_create

if TYPE_CHECKING:
    from argparse import Namespace
    from logging import Logger
    from typing import Dict, List, Optional, Sequence

    from virtbmc.config import AppConfig
    from virtbmc.driver.base import BaseBMC

    _: AppConfig = CONFIG

# The only place wher logger isn't __name__ since it can be __main__ here
log: Logger = logging.getLogger("virtbmc")


def main(args: Optional[Sequence] = None) -> None:
    # fmt: off
    parser = argparse.ArgumentParser("virtbmcd", description="Virtual BMC server for controlling virtual instances") # noqa: E501
    parser.add_argument("-V", "--version", action="version", version=importlib.metadata.version("virtbmc")) # noqa: E501
    parser.add_argument("-d","--debug", action="store_true", help="enable logging debug information to console")
    parser.add_argument("--drivers", action="store_true", help="list available drivers")
    parser.add_argument("name", action="store", nargs="*", help="names of BMCs to start")
    # fmt: on
    parsed: Namespace = parser.parse_args(args[1:] if args else None)

    if parsed.debug:
        logging.getLogger("virtbmc").setLevel(logging.DEBUG)
        log.debug("Enabled debugging from cli")

    if parsed.drivers:
        import importlib.util as util

        from virtbmc.driver import check_optional_deps

        print("Available Drivers:")
        # There's 100% better way to do it
        for driver, dependencies in check_optional_deps.items():
            has_all = True
            for dep in dependencies:
                if util.find_spec(dep) is None:
                    has_all = False
            if has_all:
                print(f" - {driver}")

    bmcs: List[BaseBMC] = []
    try:
        for file in (CONFIG.location / "bmc").iterdir():
            bmc_config = read(file)
            if bmc_config.get("name", None) in parsed.names:
                bmc = bmc_create(bmc_config)
                bmc.start()
                bmcs.append(bmc)
    except KeyboardInterrupt:
        try:
            log.info(
                "Interrupt received. Gracefully shutting down all BMCs, press ^C again to exit immediatelly."
            )
            for bmc in bmcs:
                bmc.stop()
        except KeyboardInterrupt:
            log.info("Exiting immediatelly.")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
