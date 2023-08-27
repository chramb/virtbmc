from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

try:
    import yaml
except ImportError:
    raise ImportError("Missing PyYaml")

if TYPE_CHECKING:
    from pathlib import Path


def write(config: Dict[str, Any], file: Path) -> None:
    with file.open("w") as f:
        yaml.dump(config, f)


def read(file: Path) -> Dict[str, Any]:
    with file.open("r") as f:
        return yaml.safe_load(f)
