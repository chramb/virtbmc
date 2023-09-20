from __future__ import annotations

import importlib.metadata
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Type

    from virtbmc_core.bmc import Bmc
# All convenience methods to manage BMCs


_eps = importlib.metadata.entry_points().get("virtbmc.driver")
if _eps is None:
    print("is None")
    logging.error(_eps)
    raise Exception(
        "Please install this package properly"
    )  # Only happens if driver.dummy not present

driver: Dict[str, Type[Bmc]] = {ep.name: ep.load() for ep in _eps}
