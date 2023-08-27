from __future__ import annotations

import importlib.metadata
from typing import TYPE_CHECKING

from virtbmc_core.config import CONFIG

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType
    from typing import Dict, Generator, List

    import virtbmc_core.model.bmc_config as bmc_config
    from virtbmc_core.driver.base import BaseBMC

    BmcConfig = bmc_config.BmcConfig

# All convenience methods to manage BMCs

available_drivers: Dict[str, importlib.metadata.EntryPoint] = {
    ep.name: ep for ep in importlib.metadata.entry_points().get("virtbmc.driver")  # type: ignore (this package implements dummy driver so it's never None)
}


def add(config: BmcConfig) -> BaseBMC:
    "Creates and saves BMC from given config"
    module: ModuleType = importlib.import_module(
        available_drivers[config["driver"]].load()
    )

    bmc: BaseBMC = module.driver(**config)
    bmc_config.write(config)

    return bmc


def get_config(name: str) -> BmcConfig:
    config_dict: BmcConfig = bmc_config.read(file)  # type: ignore

    # Can error if saved driver no longer exist
    return config_dict


def get(config: BmcConfig) -> BaseBMC:
    return available_drivers[config["driver"]].driver(**config)  # type: ignore


def delete(bmc: BaseBMC) -> None:
    bmc.stop(True)
    bmc_config._bmc_file(bmc.name).unlink()
    return


def load() -> Generator[BaseBMC, None, None]:
    for file in CONFIG["virtbmc"]["config_dir"].iterdir():
        config: BmcConfig = bmc_config.read()  # type: ignore
        yield get(config)


def load_all() -> List[BaseBMC]:
    return [bmc for bmc in load()]
