from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class VirtBmcError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(msg)


class VirtBmcConfigError(VirtBmcError):
    pass


class VirtBmcApiError(VirtBmcError):
    def __init__(self, code: int, message: str | None = None, data: Any | None = None) -> None:
        self.code = code
        self.msg = message
        self.data = data


class VirtBmcApiClientError(VirtBmcApiError):
    pass


class VirtBmcApiServerError(VirtBmcApiError):
    pass


class VirtBmcDaemonError(VirtBmcError):
    pass


class VirtBmcFailedToStart(VirtBmcDaemonError):
    pass


class VirtBmcFailedToStop(VirtBmcDaemonError):
    pass


class VirtBmcDbError(VirtBmcError):
    pass


class VirtBmcNotFound(VirtBmcDaemonError, VirtBmcDbError):
    pass


class VirtBmcExists(VirtBmcDaemonError, VirtBmcDbError):
    pass


class VirtBmcDriverError(VirtBmcError):
    pass
