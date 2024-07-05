from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Literal, Sequence


class CommonConfig(TypedDict):
    host: str
    drivers: Sequence[str] | None
    debug: bool


class BmcDefaultConfig(TypedDict):
    username: str
    password: str
    address: str
    port: int
    properties: dict[str, Any]


class LogConfig(TypedDict, total=False):
    mechanism: Literal["stdout", "file", "syslog"]
    show_secrets: bool
    level: int | str
    file: Path
    host: str


class DbConfig(TypedDict):
    path: str | None


class Config(TypedDict):
    virtbmc: CommonConfig
    bmc: BmcDefaultConfig
    log: Sequence[LogConfig]
    driver: dict[str, Any]
    db: DbConfig
