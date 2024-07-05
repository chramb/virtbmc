from __future__ import annotations

import logging
import os
from pathlib import Path

from virtbmc.exception import VirtBmcConfigError

log = logging.getLogger("virtbmc.config")

_VALID_PATHS = [
    "/var/lib/virtbmc/bmc",
    # XDG if Exists
    "~/.virtbmc/bmc",
]

if XDG := os.environ.get("XDG_DATA_HOME"):
    _VALID_PATHS.insert(1, XDG)

if ENV := os.environ.get("VIRTBMC_DATA"):
    _VALID_PATHS.insert(0, ENV)


def get_db_location() -> Path:
    for p in _VALID_PATHS:
        try:
            path = Path(p).expanduser()
            path.mkdir(exist_ok=True, parents=True)
            return path
        except IOError:
            msg = f"no permission to write to {p}"
            if p is not _VALID_PATHS[-1]:
                msg += " checking next valid location"

            log.debug(msg)

    msg = "Unable to find storage location for BMC's configuration"
    raise VirtBmcConfigError(msg)
    return None


DB_LOCATION = get_db_location()
log.debug(f"successfully found db location: {DB_LOCATION}")
