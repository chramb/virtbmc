from __future__ import annotations

from typing import Literal, TypedDict

from virtbmc.core.types import BmcConfig


class AmtConfig(TypedDict):
    amt_host: str
    amt_username: str | None
    amt_password: str


class AmtBmcConfig(BmcConfig):
    driver: Literal["amt"]  # type: ignore
    properties: AmtConfig  # type: ignore
