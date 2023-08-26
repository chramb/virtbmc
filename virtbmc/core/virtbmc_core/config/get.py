from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from virtbmc_core.config.serialize import read
from virtbmc_core.model import AppConfig

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Optional


def get_config_dir() -> Path:
    if p := os.environ.get("VIRTBMC_CONFIG", None):
        path: Path = Path(p).expanduser()

    try:
        # EAFP (Easier to Ask Forgiveness than Permission)
        path = Path("/etc/virtbmc")
        path.mkdir(exist_ok=True)
        return path
    except IOError:
        pass

    try:
        path = Path(
            os.environ.get("XDG_DATA_HOME", "~/.local/share/virtbmc")
        ).expanduser()
        path.mkdir(exist_ok=True, parents=True)
        return path
    except:
        raise Exception("no place to store stuff")


# TODO(Errors): handle if config is malformed
# invalid key in section(propagate from Class init)
# invalid type/value for key
def get_config() -> AppConfig:
    config_path: Optional[Path] = get_config_dir()
    if config_path is not None:
        if (config_dir := Path(config_path)).is_dir():
            for ext in ["toml", "json", "yaml", "yml", "ini", "conf"]:
                if (
                    config_file := (config_dir / "config").with_suffix("." + ext)
                ).exists():
                    return AppConfig(**read(config_file.absolute()))
        else:
            return AppConfig(**read(Path(config_path)))

    "return default config"
    return AppConfig()
