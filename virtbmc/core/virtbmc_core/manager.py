from __future__ import annotations

import importlib.metadata
from dataclasses import asdict
from typing import TYPE_CHECKING

from virtbmc_core.config import CONFIG, read, write

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType
    from typing import Dict

    from virtbmc_core.driver.base import BaseBMC
    from virtbmc_core.model import BmcConfig

# All convenience methods to manage BMCs

available_drivers: Dict[str, importlib.metadata.EntryPoint] = {
    ep.name: ep for ep in importlib.metadata.entry_points().get("virtbmc.driver")  # type: ignore (this package implements dummy driver so it's never None)
}


def _bmc_file(name: str) -> Path:
    return (CONFIG.virtbmc.config_dir / "bmc" / name).with_suffix(
        "." + CONFIG.virtbmc.storage_type
    )


def bmc_add(config: BmcConfig) -> BaseBMC:
    "Creates and saves BMC from given config"
    module: ModuleType = importlib.import_module(
        available_drivers[config["driver"]].load()
    )

    bmc: BaseBMC = module.driver(**config)

    write(config, _bmc_file(config["name"]))

    return bmc


def bmc_get_config(name: str) -> BmcConfig:
    file: Path =_bmc_file(name)
    config_dict: BmcConfig = read(file)  # type: ignore

    # Can error if saved driver no longer exist
    return config_dict


def bmc_get(config: BmcConfig) -> BaseBMC:
    return available_drivers[config["driver"]].driver(**config)  # type: ignore


def bmc_delete(bmc: BaseBMC) -> None:
    bmc.stop(True)
    _bmc_file(bmc.name).unlink()
    return


def bmc_load():
    file: Path = next(CONFIG.virtbmc.config_dir.iterdir())
    bmc_config: BmcConfig = read(file) # type: ignore
    return bmc_get(bmc_config)

        