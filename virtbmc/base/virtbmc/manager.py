from __future__ import annotations

import importlib.metadata
from dataclasses import asdict
from typing import TYPE_CHECKING

from virtbmc.config import CONFIG, read, write

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType
    from typing import Any, Dict, Generator, Type

    from virtbmc.driver.base import BaseBMC, BmcConfig

# All convenience methods to manage BMCs
available_drivers: Dict[str, Type[BaseBMC]] = {
    ep.name: ep for ep in importlib.metadata.entry_points().get("virtbmc.driver")  # type: ignore
}


def _bmc_file(name: str) -> Path:
    return (CONFIG.location / "bmc" / name).with_suffix(
        "." + CONFIG.virtbmc.storage_type
    )


# config: Type[BmcConfig]
def bmc_create(config: Dict[str, Any]) -> BaseBMC:
    return available_drivers[config.pop("driver")](**config)


def bmc_delete(bmc: BaseBMC) -> None:
    bmc.stop()
    _bmc_file(bmc.name).unlink()
    return


def bmc_load_all() -> Generator[BaseBMC, None, None]:
    for file in (CONFIG.location / "bmc").iterdir():
        yield bmc_create(**read(file))


def bmc_get_saved_config(name: str):
    for file in (CONFIG.location / "bmc").iterdir():
        config = read(file)
        if config["name"] == name:
            return config

    raise Exception("bmc with that name not found")


def bmc_save(bmc: BaseBMC):
    (CONFIG.location / "bmc").mkdir(parents=True, exist_ok=True)
    write(bmc.config(), CONFIG.location / "bmc" / f"{bmc.name}.{CONFIG.virtbmc.storage_type}")  # type: ignore
