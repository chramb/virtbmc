from __future__ import annotations

import json
from typing import TYPE_CHECKING

from virtbmc.config import CONFIG

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Iterator, Mapping, Optional, Tuple

    from virtbmc.db import Database
    from virtbmc_core.types import Config as BmcConfig
else:
    Database = object

_SUFFIX = ".json"


class JsonDB(Database):
    def __init__(self, path: Optional[Path] = None) -> None:
        self.location: Path = CONFIG["location"] / "bmc" if path is None else path
        # if errors here no place to store bmcs
        self.location.mkdir(parents=True, exist_ok=True)

    def write(self, bmc_config: BmcConfig) -> None:
        with self._file(bmc_config["name"]).open("w+") as f:
            json.dump(bmc_config, f, indent=2)

    def read(self, name: str) -> Optional[BmcConfig]:
        file = self._file(name)
        try:
            with file.open("r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            print(f"failed to read bmc config from {file.absolute()}")
            return None

    def delete(self, name: str, ok_missing: bool = False) -> None:
        self._file(name).unlink(ok_missing)

    def update(self, name: str, settings: Mapping[str, Any]) -> None:
        with self._file(name).open("r+") as f:
            config = json.load(f)
            for key, value in settings.items():
                config[key] = value
            f.seek(0)
            json.dump(config, f)
            f.truncate()
            return

    def _all(self) -> Iterator[BmcConfig]:
        for f in self.location.iterdir():
            if f.suffix == _SUFFIX:
                with f.open("r") as f:
                    yield json.load(f)

    def get_all(self) -> Tuple[BmcConfig, ...]:
        return tuple(cfg for cfg in self._all())

    def _active(self) -> Iterator[BmcConfig]:
        for f in self.location.iterdir():
            if f.suffix == _SUFFIX:
                with f.open("r") as f:
                    config = json.load(f)
                    if config.get("active", False):
                        yield config

    def get_active(self) -> Tuple[BmcConfig, ...]:
        return tuple(cfg for cfg in self._active())

    def _file(self, name: str) -> Path:
        file = self.location / (name + _SUFFIX)
        return file
