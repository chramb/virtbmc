from __future__ import annotations

from dataclasses import dataclass

from virtbmc_core.model.bmc_config import BmcConfig


@dataclass
class DummyBmcConfig(BmcConfig):
    pass
