from __future__ import annotations

from typing import Any, Literal, TypedDict

# fmt: off
ipmi_boot_device = Literal[
    'net', 'network', 'pxe', 'hd', 'safe', 'cd',
    'cdrom', 'optical', 'dvd', 'floppy','usb',
    'default', 'setup', 'bios', 'f1']
# fmt: on


class BaseBmcConfig(TypedDict):
    driver: str
    username: str
    password: str
    address: str
    port: int


class BmcConfig(BaseBmcConfig):
    name: str
    properties: dict[str, Any]


class BridgeRequest(TypedDict):
    addr: int
    channel: int


class IPMIResponse(TypedDict, total=False):
    code: int
    netfn: int
    command: int
    success: bool
    error: str
    data: bytearray


class IPMIRequest(TypedDict):
    code: int
    netfn: int
    command: int
    data: bytearray
