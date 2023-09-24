from __future__ import annotations

import importlib.metadata
from typing import TYPE_CHECKING

from virtbmc.exception import VirtBMCError

if TYPE_CHECKING:
    from typing import Dict, Type

    from virtbmc_core.bmc import Bmc
    from virtbmc_core.types import Config as BmcConfig


_eps = importlib.metadata.entry_points().get("virtbmc.driver")
if _eps is None:  # Only happens if driver.dummy not present
    raise VirtBMCError("Unable to find any VirtBMC Drivers")


driver: Dict[str, Type[Bmc]] = {ep.name: ep.load() for ep in _eps}


def make_bmc(bmc_config: BmcConfig) -> Bmc:
    config = bmc_config.copy()
    if (driver_name := config.pop("driver", None)) is None:
        raise VirtBMCError("invalid bmc config missing required: 'driver' key")
    try:
        return driver[driver_name](**config)
    except KeyError:
        raise VirtBMCError(
            f"driver with name {driver_name} not available in {driver.keys()}"
        )
