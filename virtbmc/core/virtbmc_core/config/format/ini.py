from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict
from configparser import ConfigParser

if TYPE_CHECKING:
    from pathlib import Path


def write(config: Dict[str, Any], file: Path) -> None:
    parser = ConfigParser(default_section="BMC")
    for k,v in config.items():
        parser[k] = v
    
    with file.open("w") as f:
        parser.write(f)


def read(file: Path) -> Dict[str, Any]:

    parser = ConfigParser(default_section="BMC")
    parser.read(file)

    return {s: dict(parser.items(s)) for s in parser.sections()}
