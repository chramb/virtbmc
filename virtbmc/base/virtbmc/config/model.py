from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, Any

# NOTE: to add extra config options need to either create extra class
# and make it optional in main or add parameter and add default


# in future:
# - [virtbmc]/storage_type -> storage [URI]
#
# - default /var/lib/virtbmc for root/dedicated user
#   (meaning has permission to write there
#
#   XDG_STATE_HOME for other
#
# - move config to single file ~/.config/virtbmc.*
# - store preconfigured "drivers" in different dir or same file


@dataclass
class AppGeneralConfig:
    default_driver: Optional[str] = None
    show_passwords: bool = False
    storage_type: str = "json"

    def __post_init__(self):
        if not self.default_driver and (env_driver := os.getenv("VIRTBMC_DRIVER")):
            self.default_driver = env_driver
        if not self.default_driver:
            self.default_driver = "dummy"


@dataclass
class AppServerConfig:
    address: str = "127.0.0.1"
    port: int = 50891
    # timeout: int = 5_000  # miliseconds
    # wait: int = 3_000  # miliseconds


@dataclass
class AppLogConfig:
    logfile: Optional[str] = None  # Always log without color to file
    debug: bool = False
    color: bool = True
    format: str = "{asctime} {process} {levelname} {name} [-] {message}"


@dataclass
class AppIPMIConfig:  # change to be vBMC Defaults in future
    session_timeout: int = 1  # seconds


@dataclass
class AppConfig:
    virtbmc: AppGeneralConfig = field(default_factory=AppGeneralConfig)
    server: AppServerConfig = field(default_factory=AppServerConfig)
    log: AppLogConfig = field(default_factory=AppLogConfig)
    ipmi: AppIPMIConfig = field(default_factory=AppIPMIConfig)
    location: Path = field(init=False)

    @classmethod
    def from_dict(cls, dict: Dict[str, Dict[str,Any]]):
        return AppConfig(
            virtbmc=AppGeneralConfig(**dict.get("virtbmc", {})),
            server=AppServerConfig(**dict.get("server", {})),
            log=AppLogConfig(**dict.get("log", {})),
            ipmi=AppIPMIConfig(**dict.get("ipmi", {})),
        )
