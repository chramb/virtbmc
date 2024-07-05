from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing import Literal, NotRequired

    JSONValue = dict[str, "JSONValue"] | list["JSONValue"] | str | int | float | bool | None  # fmt: skip
    Version = Literal["2.0"]
    JSON = dict[str, JSONValue] | list[JSONValue]


# Request Types
class JSONRPCRequest(TypedDict):
    jsonrpc: Version
    method: str

    id: int | None | str
    params: JSON


class JSONRPCNotification(TypedDict):
    jsonrpc: Version
    method: str

    params: NotRequired[JSON]


Request = JSONRPCRequest | JSONRPCNotification
BatchRequest = list[Request]


# Response Types
class JSONRPCSuccess(TypedDict):
    jsonrpc: Version
    id: int | None | str

    result: JSON


class ErrorType(TypedDict):
    code: int
    message: str
    data: NotRequired[JSON]


class JSONRPCError(TypedDict):
    jsonrpc: Version
    id: int | None | str

    error: ErrorType


Response = JSONRPCSuccess | JSONRPCError
BatchResponse = list[Response]
