from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, TypedDict

from virtbmc_core.config.get_config_dir import get_config_dir
from virtbmc_core.config.serialize import read as r
from virtbmc_core.config.serialize import write as w

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Dict
# from virtbmc_core.config.get import get_config_dir

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


class AppGeneralConfig(TypedDict):
    show_passwords: bool
    default_driver: str
    config_dir: Path
    storage_type: str


def app_general_config(
    config_dir: Path = get_config_dir(),
    default_driver: Optional[str] = None,
    show_passwords: bool = False,
    storage_type: str = "json",
) -> AppGeneralConfig:
    #
    if default_driver is None and (env_driver := os.environ.get("VIRTBMC_DRIVER")):
        default_driver = env_driver
    else:
        default_driver = "dummy"

    return {
        "config_dir": config_dir,
        "default_driver": default_driver,
        "show_passwords": show_passwords,
        "storage_type": storage_type,
    }


class AppServerConfig(TypedDict):
    address: str
    port: int
    timeout: int
    wait: int


def app_server_config(
    address: str = "127.0.0.1",
    port: int = 50891,
    timeout: int = 5_000,  # miliseconds
    wait: int = 3_000,  # miliseconds
) -> AppServerConfig:
    return {"address": address, "port": port, "timeout": timeout, "wait": wait}


class AppLogConfig(TypedDict):
    logfile: Optional[str]
    debug: bool
    color: bool
    format: str


AppLogConfig = TypedDict(
    "AppLogConfig",
    {"logfile": Optional[str], "debug": bool, "color": bool, "format": str},
)


def app_log_config(
    logfile: Optional[str] = None,  # Always log without color to file
    debug: bool = False,
    color: bool = True,
    format: str = "{asctime} {process} {levelname} {name} [-] {message}",
) -> AppLogConfig:
    return {"color": color, "debug": debug, "format": format, "logfile": logfile}


class AppIPMIConfig(TypedDict):
    session_timeout: int


def app_ipmi_config(session_timeout=30) -> AppIPMIConfig:
    return {"session_timeout": session_timeout}


class AppConfig(TypedDict):
    virtbmc: AppGeneralConfig
    server: AppServerConfig
    log: AppLogConfig
    ipmi: AppIPMIConfig


def init(
    virtbmc=app_general_config(),
    server=app_server_config(),
    log=app_log_config(),
    ipmi=app_ipmi_config(),
) -> AppConfig:
    return {"virtbmc": virtbmc, "server": server, "log": log, "ipmi": ipmi}


def read(file) -> AppConfig:
    read_dict: Dict[str, Any] = r(file)
    return init(**read_dict)


def write(config: AppConfig, file: Path) -> None:
    w(config, file)
