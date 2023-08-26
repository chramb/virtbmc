from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


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
