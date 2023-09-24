from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Dict

    from virtbmc.db.json import JsonDB


class _TestBMC:
    driver: str = "testing"
    # fmt: off
    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        self.cfg = kwargs
    def config(self) -> dict[str, Any]: return { **self.cfg, "driver": self.driver }
    def start(self) -> None:
        self.cfg["active"] = True
        while self.cfg["active"]:
            pass
    def stop(self) -> None:
        self.cfg["active"] = False
    # fmt: on


def _file(db: JsonDB, name: str) -> Path:
    return db.location / (name + ".json")


def _config(name: str = "name", **kwargs) -> Dict[str, Any]:  # noqa: ANN003
    config = {
        "name": name,
        "driver": "testing",
        "str": "string",
        "bool": True,
        "num": 42,
        "none": None,
        "nested": {"str": "string"},
    }
    for key, value in kwargs.items():
        config[key] = value
    return config
