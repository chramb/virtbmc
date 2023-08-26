from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict
import configparser

if TYPE_CHECKING:
    from pathlib import Path


def write(config: Dict[str, Any], file: Path) -> None:
    raise NotImplementedError


def read(file: Path) -> Dict[str, Any]:

    config = configparser.ConfigParser()
    config.read(file)

    return {s: dict(config.items(s)) for s in config.sections()}
