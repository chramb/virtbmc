from __future__ import annotations

import json
import logging
import socket
import threading
from typing import TYPE_CHECKING

from virtbmc.api._common import BUFSIZE, SEPARATOR, resolve_host
from virtbmc.api.exception import (
    InternalError,
    InvalidParams,
    JsonRPCError,
    MethodNotFound,
    ParseError,
    ServerError,
)

if TYPE_CHECKING:
    from typing import Any, Callable, NoReturn, Tuple

    from virtbmc.api.types import (
        JSON,
        JSONRPCError,
        JSONRPCNotification,
        JSONRPCRequest,
        JSONRPCSuccess,
        Request,
        Response,
    )

log: logging.Logger = logging.getLogger(__name__)


def _decode(msg: bytes) -> Request:
    try:
        return json.loads(msg)
    except json.JSONDecodeError as e:
        raise ParseError(e.msg) from e


def _encode(r: Response) -> bytes:
    return json.dumps(r).encode(encoding="utf-8")


def _build_error(
    req: JSONRPCRequest,
    exc: JsonRPCError,
    msg: str | None = None,
    data: Any | None = None,
) -> JSONRPCError:
    rsp: JSONRPCError = {
        "jsonrpc": "2.0",
        "id": req["id"] if req else None,
        "error": {"code": exc.code, "message": msg or exc.msg},
    }

    if data:
        rsp["error"]["data"] = data

    return rsp


def _build_success(req: JSONRPCRequest, res: JSON) -> JSONRPCSuccess:
    rsp: JSONRPCSuccess = {
        "jsonrpc": "2.0",
        "id": req["id"],
        "result": res or {},
    }
    return rsp


def _handle_request(r: JSONRPCRequest, mgr: Callable[..., Any]) -> bytes:
    try:
        method: Callable[..., Any] = getattr(mgr, r["method"])
        if not r["method"].startswith("_") and callable(method):
            # params not in request or nil
            if r.get("params") is None or "params" not in r:  # type: ignore
                return _encode(_build_success(r, method()))

            # list of params
            if isinstance(r["params"], list):
                return _encode(_build_success(r, method(*r["params"])))

            # json object with params
            if isinstance(r["params"], dict):  # type: ignore
                return _encode(
                    _build_success(
                        r,
                        method(**{k: v for k, v in r["params"].items() if not k.startswith("_")}),
                    )
                )

            # unexpected scenario
            raise InternalError()

        else:
            raise MethodNotFound()

    except AttributeError as e:
        # method not found
        log.error(e)
        raise MethodNotFound() from e
    except ValueError as e:
        # invalid argument type
        log.error(e)
        raise InvalidParams() from e
    except TypeError as e:
        # invalid keyword argument
        log.error(e)
        raise InvalidParams() from e
    except Exception as e:
        log.error(e)
        raise ServerError() from e


def handle_notification(n: JSONRPCNotification) -> bytes:
    return b""  # No notifications supported atm


def handle_msg(msg: bytes, mgr: Any) -> bytes | None:
    r = None
    # TODO: handle batched request
    try:
        r = _decode(msg)
        if "id" in r:
            return _handle_request(r, mgr)
        else:
            handle_notification(r)
    except JsonRPCError as e:
        if r is not None and "id" in r:
            rsp = _build_error(r, e, e.msg)
            return _encode(rsp)

        log.error(e)


def _handle_conn(conn: socket.socket, addr: Tuple[str, int], mgr: Any) -> None:
    log.debug(f"{addr} accepted connection")

    with conn:
        while msg := conn.recv(BUFSIZE):  # while new msg not empty
            while SEPARATOR not in msg:
                msg += conn.recv(BUFSIZE)
            message = msg[: -len(SEPARATOR)]
            log.debug(f"{addr} message: {message.decode()}")
            resp = handle_msg(msg[: -len(SEPARATOR)], mgr)
            if resp is not None:
                conn.sendall(resp + SEPARATOR)

    log.debug(f"{addr} connection closed")


def serve_forever(host: str, mgr: Any) -> NoReturn:
    sock_type, addr = resolve_host(host)
    with socket.socket(sock_type, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)

        sock.listen()

        while True:
            conn, addr = sock.accept()
            th = threading.Thread(target=_handle_conn, args=(conn, addr), kwargs={"mgr": mgr}, daemon=True)
            th.start()
