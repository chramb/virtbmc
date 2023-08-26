from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict  # Any  # , Dict, Union

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


def bmc_config_init(
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
