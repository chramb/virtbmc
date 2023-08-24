from dataclasses import dataclass
from typing import Any, Dict, Union

from virtbmc_core.config import CONFIG

# TODO(perf): switch all of these to typed dict and apply defaults somewhere else


@dataclass
class BmcDriverConfig:
    pass


@dataclass
class BmcConfig:
    name: str
    # bmcuuid: Optional[str]
    username: str = "admin"
    password: str = "password"
    port: int = 6230
    address: str = "::"
    driver: Union[str, Dict[str, Any]] = CONFIG.virtbmc.default_driver
