from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

try:
    import tomllib  # pyright: ignore[reportMissingImports]
except ImportError:
    import tomli as tomllib


if TYPE_CHECKING:
    from typing import Any, Dict


def get_config_location() -> Path:
    # TODO: shorten this
    if p := os.environ.get("VIRTBMC_CONFIG"):
        path: Path = Path(p).expanduser()
        try:
            path.mkdir(exist_ok=True)
            return path
        except IOError:
            pass  # TODO: add log messages

    try:
        # EAFP (Easier to Ask Forgiveness than Permission)
        path = Path("/etc/virtbmc")
        path.mkdir(exist_ok=True)
        return path
    except IOError:
        pass

    try:
        path = Path("~/.virtbmc").expanduser()
        path.mkdir(exist_ok=True, parents=True)
        return path
    except IOError:
        pass
    raise Exception("no place to store stuff")


def get_config() -> Dict[str, Any]:
    config_path: Path = get_config_location()
    if config_path is not None:
        # if there's dir under that path
        if (config_dir := Path(config_path)).is_dir():
            if (config_file := (config_dir / "config").with_suffix(".toml")).exists():
                with config_file.open("rb") as f:
                    cfg = tomllib.load(f)
                    cfg["location"] = config_path
                    return cfg
        # if there's file under that path
        else:
            with config_path.open("rb") as f:
                cfg = tomllib.load(f)
                cfg["location"] = config_path.parent
                return cfg

    return {"location": config_path}


CONFIG = get_config()
