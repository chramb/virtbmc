from __future__ import annotations

from typing import TYPE_CHECKING

from virtbmc.config._db import DB_LOCATION

if TYPE_CHECKING:
    from virtbmc.config._types import Config


DEFAULT_CONFIG: Config = {
    "virtbmc": {
        "host": "unix:///run/user/1000/virtbmcd.sock",
        # TODO: check if root or regular user and use paths based on that
        "drivers": [],  # if empty, load all
        # TODO: implement this
        "debug": False,
    },
    "bmc": {
        "username": "admin",
        "password": "password",
        "port": 623,
        "address": "::",
        "properties": {},
    },
    "log": [
        {
            "mechanism": "stdout",
            "show_secrets": False,
            "level": "INFO",
        },
    ],
    "driver": {
        "dummy": {
            # NOTE(chramb): Other drivers should be enabled by default
            "enabled": False,
        }
    },
    "db": {
        "path": str(DB_LOCATION),
    },
}
