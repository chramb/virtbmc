from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class JsonRPCError(Exception):
    code: int
    msg: str

    def __init__(self, msg: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(msg or self.msg, *args, **kwargs)

    def __str__(self) -> str:
        return f"[{self.code}] {self.msg}"


class ParseError(JsonRPCError):
    code = -32700
    msg = ("Invalid JSON was received by the server."
           "An error occurred on the server while parsing the JSON text.")  # fmt: skip


class InvalidRequest(JsonRPCError):
    code = -32600
    msg = "The JSON sent is not a valid Request object."


class MethodNotFound(JsonRPCError):
    code = -32601
    msg = "The method does not exist / is not available."


class InvalidParams(JsonRPCError):
    code = -32602
    msg = "Invalid method parameter(s)."


class InternalError(JsonRPCError):
    code = -32603
    msg = "Internal JSON-RPC error."


class ServerError(JsonRPCError):
    code = -32000  # to -32099
    msg = "Reserved for implementation-defined server-errors."
