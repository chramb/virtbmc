from __future__ import annotations

from typing import TYPE_CHECKING
import os

from dataclasses import asdict
from virtbmc.log import log_configure
from virtbmc.config.format import read, write
from pathlib import Path
from virtbmc.config.model import AppConfig

if TYPE_CHECKING:
    from typing import List
    from typing import Optional


def get_config_location() -> Path:
    # TODO: shorten this
    if p := os.environ.get("VIRTBMC_CONFIG"):
        path: Path = Path(p).expanduser()
        try:
            path.mkdir(exist_ok=True)
            return path
        except IOError as e:
            pass  # TODO: add log messages

    try:
        # EAFP (Easier to Ask Forgiveness than Permission)
        path = Path("/etc/virtbmc")
        path.mkdir(exist_ok=True)
        return path
    except IOError as e:
        pass

    try:
        path = Path(
            os.environ.get("XDG_DATA_HOME", "~/.local/share/virtbmc")
        ).expanduser()
        path.mkdir(exist_ok=True, parents=True)
        return path
    except IOError as e:
        pass
    raise Exception("no place to store stuff")


# TODO(Errors): handle if config is malformed
# invalid key in section(propagate from Class init)
# invalid type/value for key
def get_config() -> AppConfig:
    config_path: Path = get_config_location()
    if config_path is not None:
        # if there's dir under that path
        if (config_dir := Path(config_path)).is_dir():
            for ext in ["toml", "json", "yaml", "yml", "ini", "conf"]:
                if (
                    config_file := (config_dir / "config").with_suffix("." + ext)
                ).exists():
                    cfg = AppConfig.from_dict(read(config_file.absolute()))
                    cfg.location = config_path
                    return cfg
        # if there's file under that path
        else:
            cfg = AppConfig.from_dict(read(config_path.absolute()))
            cfg.location = config_path.parent
            return cfg

    "return default config"
    cfg = AppConfig()
    cfg.location = Path("~/.virtbmc/")
    cfg.location.mkdir(parents=True, exist_ok=True)
    return cfg


CONFIG: AppConfig = get_config()
(CONFIG.location / "bmc").mkdir(parents=True, exist_ok=True)
log_configure(CONFIG)
