from __future__ import annotations

import importlib
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing import Any, Dict, Protocol, Union

    from virtbmc.config.model import AppConfig
    from virtbmc.driver.base import BmcConfig

    # fmt: off
    class ConfigOperations(Protocol):
        def write(self, config: Dict[str, Any], file: Path) -> None:...
        def read(self, file: Path) -> Dict[str, Any]:...
    # fmt: on

# in future:
# - add support for storing all bmcs in single file (if [virtbmc]/storage has no {name})

modules: Dict[str, str] = {
    "json": "virtbmc.config.format.json",
    "ini": "virtbmc.config.format.ini",
    "conf": "virtbmc.config.format.ini",
    "toml": "virtbmc.config.format.toml",
    "yaml": "virtbmc.config.format.yml",
    "yml": "virtbmc.config.format.yml",
}


def read(file: Path) -> Dict[str, Any]:
    # TODO: add overload depending on path that returns BmcConfig or AppConfig
    if file.suffix in modules:
        # I have no idea how to properly type it
        return importlib.import_module(file.suffix).read(file)
    else:
        raise Exception("invalid filetype")


def write(config: Dict[str, Any], file: Path) -> None:
    # TODO: add switch for saving only non default values
    try:
        importlib.import_module(modules[file.suffix]).write(config, file)
    except KeyError:
        raise Exception("Unsupported/Invalid file format")
