from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from pathlib import Path


def write(config: Dict[str, Any], file: Path) -> None:
    with file.open("w") as f:
        json.dump(config, f)
        return


def read(file: Path) -> Dict[str, Any]:
    with file.open("r") as f:
        return json.load(f)
