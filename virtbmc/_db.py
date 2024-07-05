from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from virtbmc.config import get_config_value
from virtbmc.exception import VirtBmcConfigError

if TYPE_CHECKING:
    from typing import Any, Iterator, Mapping, Unpack

    from virtbmc.core.types import BmcConfig

log = logging.getLogger("virtbmc.db")

try:
    location = Path(get_config_value("db.path"))  # type: ignore
except TypeError as e:
    msg = "Invalid value for db.path configuration"
    raise VirtBmcConfigError(msg) from e

_SUFFIX = ".json"


def _file(name: str) -> Path:
    file = location / (name + _SUFFIX)
    return file


def _all() -> Iterator[BmcConfig]:
    for f in location.iterdir():
        if f.suffix == _SUFFIX:
            with f.open("r") as f:
                yield json.load(f)


def init() -> None:
    # if errors here no place to store bmcs
    location.mkdir(parents=True, exist_ok=True)


def create(**bmc_config: Unpack[BmcConfig]) -> None:
    with _file(bmc_config["name"]).open("w+") as f:
        json.dump(bmc_config, f, indent=2)


def delete(name: str, missing_ok: bool = False) -> None:
    return _file(name).unlink(missing_ok)


def update(name: str, settings: Mapping[str, Any]) -> None:
    with _file(name).open("r+") as f:
        config: BmcConfig = json.load(f)
        for key, value in settings.items():
            if key != "properties":
                config[key] = value
            else:
                config["properties"].update(value)
        f.seek(0)
        json.dump(config, f)
        f.truncate()
        return


def start(name: str) -> None:
    return update(name, {"properties": {"active": True}})


def stop(name: str) -> None:
    return update(name, {"properties": {"active": False}})


def list(only_active: bool = False) -> tuple[BmcConfig, ...]:
    if only_active:
        return tuple(cfg for cfg in _all() if cfg["properties"].get("active", False))
    else:
        return tuple(cfg for cfg in _all())


def show(name: str) -> BmcConfig | None:
    file = _file(name)
    try:
        with file.open("r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        log.error(f"failed to decode bmc config from {file.absolute()}")
        return None
