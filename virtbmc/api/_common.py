from __future__ import annotations

import socket
import urllib.parse
from ipaddress import ip_address
from pathlib import Path
from typing import TYPE_CHECKING

from virtbmc.exception import VirtBmcConfigError

if TYPE_CHECKING:
    from typing import Tuple

BUFSIZE = 1024
SEPARATOR = b"\n"
DEFAULT_PORT = 5497


def resolve_host(host: str) -> Tuple[socket.AddressFamily, socket._Address]:  # type: ignore
    try:
        url = urllib.parse.urlsplit(host)
    except ValueError:
        msg = "Invalid value for host flag"
        raise VirtBmcConfigError(msg)
    if url.scheme == "unix":
        try:
            path = Path(url.path)
        except Exception:
            msg = "Invalid path section in the host argument"
            raise VirtBmcConfigError(msg)

        if not path.parent.exists():
            msg = f"Path {path.parent} does not exist"
            raise VirtBmcConfigError(msg)

        return socket.AF_UNIX, (str(path))

    if url.scheme == "tcp":
        hostname = url.hostname
        if hostname is None:
            msg = "Missing hostname section of host argument"
            raise VirtBmcConfigError(msg)

        addr = socket.gethostbyname(hostname)
        port = url.port or DEFAULT_PORT

        if ip_address(addr).version == 4:
            return socket.AF_INET, (addr, port)

        if ip_address(addr).version == 6:
            return socket.AF_INET6, (addr, port)

    msg = "invalid url scheme in host argument"
    raise VirtBmcConfigError(msg)
