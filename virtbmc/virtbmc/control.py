"""Module responsible for managing all BMCs."""
# ruff: noqa: ANN401
from __future__ import annotations

from typing import TYPE_CHECKING

from virtbmc.db.json import JsonDB
from virtbmc.driver import make_bmc
from virtbmc.manager import threading

if TYPE_CHECKING:
    from typing import Optional, Tuple

    from virtbmc.db import Database
    from virtbmc.manager import Manager
    from virtbmc_core.types import Config as BmcConfig

# in future create single connection and reuse it
manager: Manager = threading  # TODO: support different when config is finished
db: Database = JsonDB()
save_defaults: bool = True  # should be config option


def init() -> None:
    for bmc_config in db.get_active():
        manager.start(bmc_config["name"])


def create(bmc_config: BmcConfig) -> None:
    if "name" not in bmc_config:
        raise Exception("invalid bmc config missing key: 'name'")
    if "driver" not in bmc_config:
        raise Exception("invalid bmc config missing key: 'driver'")
    if manager.get(bmc_config["name"]) or db.read(bmc_config["name"]):
        raise Exception("Bmc with that name already exists")
    config = make_bmc(bmc_config).config()  # validates config and driver
    db.write(config)  # driver will overwrite so we don't care
    return


def delete(name: str) -> None:
    if manager.get(name) is not None:
        # ? TODO: error here and add --force in the future
        manager.stop(name)
        manager.delete(name)
    try:
        db.delete(name)  # db doesn't care if doesn't exist
    except FileNotFoundError:
        raise Exception("bmc with that name doesn't exist")


# TODO: error checking
def start(name: str) -> None:
    config = db.read(name)
    if config is None:
        raise Exception("bmc with that name doesn't exist")
    manager.create(config)
    try:
        manager.start(name)
    except PermissionError:
        raise Exception("Permission denied to start booho")
    db.update(name, {"active": True})
    return


def stop(name: str) -> None:
    running_config = manager.get(name)
    if running_config is None:
        raise Exception("No BMC with that name is active")
    manager.stop(name)
    manager.delete(name)
    db.update(name, {"active": False})


def get(name: str) -> Optional[BmcConfig]:
    return db.read(name)


def get_all() -> Tuple[BmcConfig, ...]:
    return tuple(x for x in db.get_all())
