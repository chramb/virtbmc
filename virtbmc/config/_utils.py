from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from virtbmc.config._default import DEFAULT_CONFIG
from virtbmc.exception import VirtBmcConfigError

try:
    import tomllib  # pyright: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # pyright: ignore

if TYPE_CHECKING:
    from typing import Any, Dict, Final

    from virtbmc.config._types import Config

log = logging.getLogger("virtbmc.config")


if TYPE_CHECKING:
    from typing import Any, Dict


_VALID_PATHS = ["/etc/virtbmc/", "~/.virtbmc/"]
if ENV := os.environ.get("VIRTBMC_CONFIG"):
    _VALID_PATHS.insert(0, ENV)


def get_config_location() -> Path | None:
    for p in _VALID_PATHS:
        try:
            path = Path(p).expanduser()
            path.mkdir(exist_ok=True, parents=True)
            return path
        except IOError:
            msg = f"no permission to write to {p}"
            if p is not _VALID_PATHS[-1]:
                msg += " checking next valid location"

            log.debug(msg)

    msg = "Unable to find storage location for BMC's configuration"
    log.debug(msg)
    return None


CONFIG_LOCATION: Final[Path | None] = get_config_location()
if CONFIG_LOCATION:
    log.debug(f"successfully found config location: {CONFIG_LOCATION}")


def _get_config() -> Config:
    config_path = CONFIG_LOCATION
    if config_path is not None:
        # if there's dir under that path
        if (config_dir := Path(config_path)).is_dir():
            if (config_file := (config_dir / "config").with_suffix(".toml")).exists():
                with config_file.open("rb") as f:
                    return tomllib.load(f)  # type: ignore
        # if there's file under that path
        else:
            with config_path.open("rb") as f:
                return tomllib.load(f)  # type: ignore

    return DEFAULT_CONFIG


CONFIG: Config = _get_config()


def get_config_value(path: str, config: Config = CONFIG) -> Any | Dict[str, Any]:
    # TODO: Handle errors better
    # TODO: support showing config in cli
    keys = path.split(".")
    data = config  # type: ignore

    for key in keys:
        if isinstance(data, dict):
            if key in data:
                data = data[key]  # type: ignore
            else:
                if config is DEFAULT_CONFIG:
                    raise VirtBmcConfigError(f"Value '{path}' not found in Config and Default Config")

                data = get_config_value(DEFAULT_CONFIG, path)  # type: ignore
                break
        elif isinstance(data, list):
            keyInt = int(key)
            data: list[Any]
            if len(data) > keyInt:
                data = data[keyInt]
            else:
                raise VirtBmcConfigError("Invalid value for List section of config")
        else:
            raise VirtBmcConfigError("Trying to walk over non dict type")

    return data  # type: ignore
