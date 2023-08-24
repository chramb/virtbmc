from __future__ import annotations

# TODO: split filetypes to different files, load with importlib
import os
from pathlib import Path
from typing import TYPE_CHECKING

from virtbmc_core.model import AppConfig
from virtbmc_core.log import configure_logs

if TYPE_CHECKING:
    from typing import Any, Dict, Final

_CONFIG_FILE_PATHS: tuple[str, str, str] = (
    os.environ.get("VIRTBMC_CONFIG", ""),
    os.path.join(
        os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share/virtbmc")),
        ".virtbmc",
    ),
    "/etc/virtbmc/",
)
# TODO(config): rewrite to work nicer both ^V
CONFIG_PATH: Final[os.PathLike[str] | None] = next(  # type: ignore
    (x for x in _CONFIG_FILE_PATHS if os.path.exists(x)), None
)


def _get_config():
    if CONFIG_PATH is not None:
        if (config_dir := Path(CONFIG_PATH)).is_dir():
            for ext in ["toml", "json", "yaml", "yml", "ini", "conf"]:
                if (config_file := (config_dir / "config").with_suffix(ext)).exists():
                    return AppConfig(**read(config_file.absolute()))
        else:
            return AppConfig(**read(Path(CONFIG_PATH)))

    "return default config"
    return AppConfig()


CONFIG = _get_config()


def write(config: Dict[str, Any], path: Path) -> None:
    suffix = str(CONFIG.virtbmc.storage_type)

    if suffix == "toml":
        try:
            import tomli_w  # pyright: ignore[reportMissingImports]
        except ImportError:
            raise ImportError("Missing tomli-w library")

        with path.open("wb") as f:
            tomli_w.dump(config, f)
            return

    if suffix == "json":
        import json

        with path.open("w") as f:
            json.dump(config, f)
            return

    if suffix in ["yaml", "yml"]:
        try:
            import yaml  # pyright: ignore[reportMissingModuleSource]
        except ImportError:
            raise ImportError("Missing PyYaml library")

        with path.open("w") as f:
            yaml.dump(config, f)
            return

    if suffix in ["ini", "conf"]:
        raise NotImplementedError


def read(file: Path) -> Dict[str, Any]:
    if file.suffix == "toml":
        try:
            import tomllib  # pyright: ignore[reportMissingImports]
        except ImportError:
            try:
                import tomli as tomllib  # pyright: ignore[reportMissingImports]
            except ImportError:
                raise ImportError("error using toml format without parsing library")

        with file.open("rb") as f:
            return tomllib.load(f)

    if file.suffix == "json":
        import json

        with file.open("r") as f:
            return json.load(f)

    if file.suffix in ["yaml", "yml"]:
        try:
            import yaml  # pyright: ignore[reportMissingModuleSource]
        except ImportError:
            raise ImportError("Missing PyYaml library")

        with file.open("r") as f:
            return yaml.safe_load(f)

    if file.suffix in ["ini", "conf"]:
        import configparser

        config = configparser.ConfigParser()
        config.read(file)

        return {s: dict(config.items(s)) for s in config.sections()}

    return {}

configure_logs(CONFIG)