from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Optional

from pyghmi.ipmi.bmc import Bmc

if TYPE_CHECKING:
    import threading
    from typing import Literal

__all__ = ["BaseBMC"]


def _fix_not_implemented(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotImplementedError:
            return -1  # TODO: check if correct constant (test with ipmitool)

    return wrapper


def _handle_not_implemented_methods(cls):
    for name, val in vars(cls).items():
        if callable(val) and not name.startswith("__"):
            setattr(cls, name, _fix_not_implemented(val))
    return cls


@_handle_not_implemented_methods
class BaseBMC(Bmc):
    thread: threading.Thread

    def __init__(
        self,
        name: str,
        username: str = "admin",
        password: str = "password",
        port: int = 623,
        address: str = "::",
        bmcuuid: Optional[str] = None,
    ) -> None:
        self.name = name
        self.started = False
        super().__init__({username: password}, port, bmcuuid, address)

    def cold_reset(self, managed=False) -> Literal[0]:
        return 0

    def start(self, timeout: int) -> None:
        self.listen()

    def stop(self, managed: bool = False) -> Literal[0]:
        return self.cold_reset()
