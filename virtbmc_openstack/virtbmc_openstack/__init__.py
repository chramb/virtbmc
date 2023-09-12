from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from virtbmc_openstack.bmc.cached import CachedBMC
from virtbmc_openstack.bmc.safe import SafeBMC
from virtbmc_openstack.bmc.simple import SimpleBMC
from virtbmc_openstack.bmc.unsafe import UnsafeBMC

if TYPE_CHECKING:
    from typing import Literal, Optional

    from virtbmc_openstack.bmc import BaseOpenStackBMC


class OpenstackBMCConfig(TypedDict):
    name: str
    mode: Literal["safe", "unsafe", "cached", "simple"]
    cloud: Optional[str]
    username: str
    password: str
    port: int
    address: str


def OpenStackBMC(
    name: str,
    cloud: Optional[str],
    mode: Literal["safe", "unsafe", "cached", "simple"],
    username: str = "admin",
    password: str = "password",
    port: int = 623,
    address: str = "::",
    _wait_for_idle: bool = True,
) -> BaseOpenStackBMC:
    kwargs: OpenstackBMCConfig = {
        "name": name,
        "mode": mode,
        "cloud": cloud,
        "username": username,
        "password": password,
        "port": port,
        "address": address,
    }
    if mode == "safe":
        return SafeBMC(**kwargs)
    if mode == "unsafe":
        return UnsafeBMC(**kwargs)
    if mode == "cached":
        return CachedBMC(**kwargs)
    if mode == "simple":
        return SimpleBMC(**kwargs)

    raise ValueError("Invalid mode specified")
