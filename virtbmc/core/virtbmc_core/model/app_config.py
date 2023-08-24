from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# NOTE: to add extra config options need to either create extra class
# and make it optional in main or add parameter and add default


@dataclass
class AppGeneralConfig:
    show_passwords: bool = False
    default_driver: str = "dummy"
    config_dir: Path = field(default_factory=Path)
    storage_type: str = "toml"  # add sqlite support in future

    def __post_init__(self):
        if isinstance(self.config_dir, str):
            self.config_dir = Path(self.config_dir).expanduser()

        if not self.default_driver and (env_driver := os.environ.get("VIRTBMC_DRIVER")):
            self.default_driver = env_driver


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

    # TODO(Errors): handle if config is malformed
    # invalid key in section(propagate from Class init)
    # invalid type/value for key
