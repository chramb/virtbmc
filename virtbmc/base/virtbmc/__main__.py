from __future__ import annotations

import argparse
import importlib.metadata
import logging
import sys
from typing import TYPE_CHECKING

from virtbmc.config import CONFIG
from virtbmc.manager import bmc_load_all

if TYPE_CHECKING:
    from argparse import Namespace
    from logging import Logger
    from typing import Dict, Optional, Sequence

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
    parser.add_argument("--no-autostart", action="store_true", help="don't start BMCs configured with 'autostart=true'")
    parser.add_argument("name", action="store", nargs="*", help="names of BMCs to start")
    # fmt: on
    parsed: Namespace = parser.parse_args(args[1:] if args else None)
    if parsed.debug:
        logging.getLogger("virtbmc").setLevel(logging.DEBUG)
        log.debug("Enabled debugging from cli")
    try:
        bmcs: Dict[str, BaseBMC] = {bmc.name: bmc for bmc in bmc_load_all()}
        for bmc in bmcs.values():
            if bmc.autostart and not parsed.no_autostart:
                bmc.start()

        for name in parsed.name:
            try:
                bmcs[name].start() if bmcs[name]._started == False else None
                bmc = bmcs.pop(name)
            except KeyError:
                log.info(f"Invalid BMC name: {name}, skipping")
    except KeyboardInterrupt:
        try:
            log.info(
                "Interrupt received. Gracefully shutting down all BMCs, press ^C again to exit immediatelly."
            )
            ...  # Stop running BMCs
        except KeyboardInterrupt:
            log.info("Exiting immediatelly.")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
