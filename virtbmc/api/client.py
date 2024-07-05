from __future__ import annotations

import json
import socket

# TODO: fix the _host and HOST and config.host and cli host mess
from typing import TYPE_CHECKING, Sequence

from virtbmc.api._common import BUFSIZE, SEPARATOR, resolve_host
from virtbmc.config import get_config_value
from virtbmc.exception import VirtBmcApiClientError

if TYPE_CHECKING:
    from typing import Unpack

    from virtbmc.api.types import JSON, Request, Response
    from virtbmc.core.types import BmcConfig

    listType = list


_host: str = get_config_value("virtbmc.host")  # type: ignore
counter: int = 1


def call(method: str, params: JSON, host: str) -> Response:
    global counter
    counter += 1
    return _send_msg(
        message={
            "jsonrpc": "2.0",
            "id": counter,
            "method": method,
            "params": params,
        },
        host=host,
    )


def _send_msg(message: Request, host: str = _host) -> Response:  # type: ignore
    sock_type, addr = resolve_host(host)
    with socket.socket(sock_type, socket.SOCK_STREAM) as sock:
        sock.connect(addr)
        sock.sendall(json.dumps(message).encode() + SEPARATOR)
        resp = sock.recv(BUFSIZE)
        while SEPARATOR not in resp:
            resp += sock.recv(BUFSIZE)
        return json.loads(resp)


def _name_call(method: str, name: str) -> Response:
    return call(
        method=method,
        params={"name": name},
        host=_host,
    )


def create(**bmc_config: Unpack[BmcConfig]) -> None:
    result = call(
        method="create",
        params=bmc_config,  # type: ignore
        host=_host,
    )
    if "error" in result:
        raise VirtBmcApiClientError(**result["error"])
    else:
        return result["result"]  # type: ignore


def start(name: str) -> None:
    result = _name_call("start", name)
    if "error" in result:
        raise VirtBmcApiClientError(**result["error"])
    else:
        return result["result"]  # type: ignore


def stop(name: str) -> None:
    result = _name_call("stop", name)
    if "error" in result:
        raise VirtBmcApiClientError(**result["error"])
    else:
        return result["result"]  # type: ignore


def delete(name: str) -> None:
    result = _name_call("delete", name)
    if "error" in result:
        raise VirtBmcApiClientError(**result["error"])
    else:
        return result["result"]  # type: ignore


def show(name: str) -> BmcConfig | None:
    result = _name_call("show", name)
    if "error" in result:
        raise VirtBmcApiClientError(**result["error"])
    else:
        return result["result"]  # type: ignore


def list(only_active: bool = False) -> Sequence[BmcConfig]:
    result = call(
        method="list",
        params={"only_active": only_active},
        host=_host,
    )
    if "error" in result:
        raise VirtBmcApiClientError(**result["error"])
    else:
        return result["result"]  # type: ignore
