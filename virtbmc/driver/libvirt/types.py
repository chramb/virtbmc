from __future__ import annotations

from typing import Literal, Optional, TypedDict

from virtbmc.core.types import BmcConfig


class LibvirtBmcConfig(BmcConfig):
    driver: Literal["libvirt"]  # type: ignore
    properties: LibvirtConfig  # type: ignore


class LibvirtConfig(TypedDict):
    libvirt_uri: Optional[str]
    libvirt_sasl_username: Optional[str]
    libvirt_sasl_password: Optional[str]
