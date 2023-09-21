"""Module responsible for managing all BMCs."""
# ruff: noqa: ANN401
from __future__ import annotations

from typing import TYPE_CHECKING

from virtbmc.db.toml import TomlDB
from virtbmc.driver import driver
from virtbmc.manager import threading

if TYPE_CHECKING:
    from typing import Optional, Tuple

    from virtbmc.db import Database
    from virtbmc.manager import Manager
    from virtbmc_core.types import Config as BmcConfig

# in future create single connection and reuse it
manager: Manager = threading  # TODO: support different when config is finished
db: Database = TomlDB()
save_defaults: bool = True  # should be config option


def init() -> None:
    for bmc_config in db.get_active():
        manager.start(bmc_config["name"])


def create(bmc_config: BmcConfig) -> None:
    if not isinstance(bmc_config.get("driver"), str):
        raise Exception("invalid bmc config")
    if not isinstance(name := bmc_config.get("name"), str):
        raise Exception("invalid bmc config")
    if db.read(name):
        raise Exception("bmc already exists")
    # V-- validation
    full_bmc_config = driver[bmc_config.pop("driver")](**bmc_config).config()
    config: BmcConfig = full_bmc_config if save_defaults else bmc_config

    db.create(config)
    return


def delete(name: str) -> None:
    manager.delete(name)
    db.delete(name)
    return


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
    # db.start(name)
    return


def stop(name: str) -> None:
    manager.stop(name)
    db.stop(name)
    return


def get(name: str) -> Optional[BmcConfig]:
    return db.read(name)


def get_all() -> Tuple[BmcConfig, ...]:
    return tuple(x for x in db.get_all())
