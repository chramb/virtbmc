from __future__ import annotations

from typing import TYPE_CHECKING

import tomli_w

try:
    import tomllib  # pyright: ignore[reportMissingImports]
except ImportError:
    import tomli as tomllib

from virtbmc.config import CONFIG

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Generator, Optional

    from virtbmc.db import Database
    from virtbmc_core.types import Config as BmcConfig
else:
    Database = object


class TomlDB(Database):
    def __init__(self) -> None:
        self.db: Path = CONFIG["location"] / "bmc"
        # if errors here no place to store bmcs
        (CONFIG["location"] / "bmc").mkdir(parents=True, exist_ok=True)

    def create(self, bmc_config: BmcConfig) -> None:
        self._file(bmc_config["name"]).touch()
        with self._file(bmc_config["name"]).open("wb") as f:
            bmc_config["active"] = False
            tomli_w.dump(bmc_config, f)

    def read(self, name: str) -> Optional[BmcConfig]:
        file = self._file(name)
        if file.exists():
            with file.open("rb") as f:
                return tomllib.load(f)
        else:
            return None

    def delete(self, name: str) -> None:
        self._file(name).unlink()

    def start(self, name: str) -> None:
        with self._file(name).open("wb") as f:
            config = tomllib.load(f)
            print(config)
            config["active"] = True
            tomli_w.dump(config, f)
            return

    def stop(self, name: str) -> None:
        with self._file(name).open("wb") as f:
            config = tomllib.load(f)
            config["active"] = False
            tomli_w.dump(config, f)
            return

    def all(self) -> Generator[BmcConfig, None, None]:
        for fl in self.db.iterdir():
            if fl.suffix == ".toml":
                with fl.open("rb") as f:
                    yield tomllib.load(f)

    def _file(self, name: str) -> Path:
        return self.db / (name + ".toml")
