from __future__ import annotations

import importlib.metadata
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Type

    from virtbmc_core.bmc import Bmc
    from virtbmc_core.types import Config as BmcConfig
# All convenience methods to manage BMCs


_eps = importlib.metadata.entry_points().get("virtbmc.driver")
if _eps is None:  # Only happens if driver.dummy not present
    raise Exception("Please install this package properly")


driver: Dict[str, Type[Bmc]] = {ep.name: ep.load() for ep in _eps}


def make_bmc(bmc_config: BmcConfig) -> Bmc:
    config = bmc_config.copy()
    if (driver_name := config.pop("driver", None)) is None:
        raise Exception("invalid bmc config missing required: 'driver' key")
    try:
        return driver[driver_name](**config)
    except KeyError:
        raise Exception(
            f"driver with name {driver_name} not available in {driver.keys()}"
        )
