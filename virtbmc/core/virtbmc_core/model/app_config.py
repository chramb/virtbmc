from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional, TypedDict, NotRequired

#from virtbmc_core.config.get import get_config_dir

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

class TDAppConfig(TypedDict):
    virtbmc: TDAppGeneralConfig
    server: TDAppServerConfig
    log: TDAppLogConfig
    ipmi: TDAppIPMIConfig

class TDAppGeneralConfig(TypedDict):
    show_passwords: bool
    default_driver: str
    config_dir: Path
    storage_type: str

class TDAppServerConfig(TypedDict):
    address: str
    port: int
    timeout: int
    wait: int

class TDAppLogConfig(TypedDict):
    ...
class TDAppIPMIConfig(TypedDict):
    ...
@dataclass
class AppGeneralConfig:
    show_passwords: bool = False
    default_driver: str = "dummy"
    config_dir: Path = field(default_factory=Path)
    storage_type: str = "json"

    def __post_init__(self):
        if not self.default_driver and (env_driver := os.environ.get("VIRTBMC_DRIVER")):
            self.default_driver = env_driver

        return asdict(self)


@dataclass
class AppServerConfig:
    address: str = "127.0.0.1"
    port: int = 50891
    timeout: int = 5_000  # miliseconds
    wait: int = 3_000  # miliseconds


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
