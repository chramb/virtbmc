from __future__ import annotations

import configparser
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from pathlib import Path


def write(config: Dict[str, Any], file: Path) -> None:
    parser = configparser.ConfigParser()
    for key in config.keys():
        parser.add_section(key)

    for k, v in config.items():
        parser[k] = v

    with file.open("w") as f:
        parser.write(f)


def read(file: Path) -> Dict[str, Any]:
    config = configparser.ConfigParser()
    config.read(file)

    cfg = {s: dict(config.items(s)) for s in config.sections()}
    if virtbmc := cfg.get("virtbmc"):
        return virtbmc
    else:
        return cfg
