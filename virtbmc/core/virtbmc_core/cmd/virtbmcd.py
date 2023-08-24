from __future__ import annotations

import argparse
import importlib.metadata
import logging
import sys
from typing import TYPE_CHECKING

from virtbmc_core.config import CONFIG

if TYPE_CHECKING:
    from typing import Optional, Sequence

_ = CONFIG  # configures everything before starting app
log = logging.getLogger("virtbmc.core")


def main(args: Optional[Sequence] = None) -> None:
    # fmt: off
    parser = argparse.ArgumentParser("virtbmcd", description="A virtual BMC server for controlling virtual instances") # noqa: E501
    parser.add_argument("-V", "--version", action="version", version=importlib.metadata.version("virtbmc_core")) # noqa: E501
    parser.add_argument("--debug", action="store_true")
    # fmt: on
    parsed = parser.parse_args(args[1:] if args else None)
    if parsed.debug:
        logging.getLogger("virtbmc.core").setLevel(logging.DEBUG)
        log.debug("Enabled debugging from cli")
    try:
        # DO Stuff
        from virtbmc_core.model.bmc_config import BmcConfig

        print(vars(BmcConfig("hello", driver={"A:": 1})))
    except KeyboardInterrupt:
        log.debug("received keyboard interrupt, exiting")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
