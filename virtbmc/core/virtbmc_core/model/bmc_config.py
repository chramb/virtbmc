from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict  # Any  # , Dict, Union

from virtbmc_core.config.get_config import CONFIG
from virtbmc_core.config.serialize import read as r
from virtbmc_core.config.serialize import write as w

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Dict

# class BmcDriverConfig:  # Turn this into typing.protocol in future
#     def __init__(self):
#         raise Exception("this class isn't supposed to be used directly")


class BmcConfig(TypedDict):
    name: str
    # bmcuuid: Optional[str]
    username: str
    password: str
    port: int
    address: str
    driver: str
    autostart: bool

    # Log { enabled, file/endpoint, level}
    # driver: Union[str, BmcDriverConfig] = CONFIG.virtbmc.default_driver


def init(
    name: str,
    # bmcuuid: Optional[str]
    username: str = "admin",
    password: str = "password",
    port: int = 6230,
    address: str = "::1",
    driver: str = "",
    autostart: bool = False,
) -> BmcConfig:
    return {
        "name": name,
        "username": username,
        "password": password,
        "port": port,
        "address": address,
        "driver": driver,
        "autostart": autostart,
    }


def _bmc_file(name: str) -> Path:
    return (CONFIG["virtbmc"]["config_dir"] / "bmc" / name).with_suffix(
        "." + CONFIG["virtbmc"]["storage_type"]
    )


def read(name: str) -> BmcConfig:
    read_dict: Dict[str, Any] = r(_bmc_file(name))
    return init(**read_dict)


def write(config: BmcConfig) -> None:
    w(config, _bmc_file(config["name"]))
