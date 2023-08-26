from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import virtbmc_core.model.app_config as app_config
from virtbmc_core.config.get_config_dir import get_config_dir
from virtbmc_core.config.serialize import read

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Optional


# TODO(Errors): handle if config is malformed
# invalid key in section(propagate from Class init)
# invalid type/value for key
def get_config() -> app_config.AppConfig:
    config_path: Optional[Path] = get_config_dir()
    if config_path is not None:
        if (config_dir := Path(config_path)).is_dir():
            for ext in ["toml", "json", "yaml", "yml", "ini", "conf"]:
                if (
                    config_file := (config_dir / "config").with_suffix("." + ext)
                ).exists():
                    return app_config.read(config_file)
        else:
            "fallback if somebody points to file with env var"
            return app_config.read(Path(config_path))

    "return default config"
    return app_config.init()


CONFIG = get_config()
