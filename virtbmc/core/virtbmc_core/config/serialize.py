from __future__ import annotations

import importlib
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing import Any, Dict, Protocol, Union

    from virtbmc_core.model.app_config import AppConfig
    from virtbmc_core.model.bmc_config import BmcConfig

    # fmt: off
    class ConfigOperations(Protocol):
        def write(self, config: Dict[str, Any], file: Path) -> None:...
        def read(self, file: Path) -> Dict[str, Any]:...
    # fmt: on

# in future:
# - add support for storing all bmcs in single file (if [virtbmc]/storage has no {name})

modules: Dict[str, str] = {
    "toml": "virtbmc_core.config.format.toml",
    "yaml": "virtbmc_core.config.format.yml",
    "yml": "virtbmc_core.config.format.yml",
    "ini": "virtbmc_core.config.format.ini",
    "conf": "virtbmc_core.config.format.ini",
    "json": "virtbmc_core.config.format.json",
}


def read(file: Path) -> Dict[str, Any]:  #  Union[BmcConfig, AppConfig]:
    if file.suffix in modules:
        # I have no idea how to properly type it
        return importlib.import_module(file.suffix).read(file)  # type: ignore
    else:
        raise Exception("invalid filetype")


def write(config: Union[BmcConfig, AppConfig], file: Path) -> None:
    # TODO: add switch for saving only non default values
    try:
        importlib.import_module(modules[file.suffix]).write(config, file)  # type: ignore
    except KeyError:
        raise Exception("Unsupported/Invalid file format")
