from __future__ import annotations

import functools
import threading
from dataclasses import dataclass, field, fields
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
@dataclass
class BaseBMC(Bmc):
    name: str
    username: str = "admin"
    password: str = "password"
    port: int = 6230
    address: str = "::1"
    autostart: bool = False
    bmcuuid: Optional[str] = field(default=None)

    thread: threading.Thread = field(init=False)

    def __post_init__(self):
        super().__init__(
            {self.username: self.password}, self.port, self.bmcuuid, self.address
        )
        self.thread = threading.Thread(target=self.start)

    def cold_reset(self, managed=False) -> Literal[0]:
        return 0

    def start(self, timeout: int) -> None:
        if not self.thread.is_alive():
            self.listen()

    def stop(self, managed: bool = False) -> Literal[0]:
        return self.cold_reset()

    def config(self):
        return {f.name: getattr(self, f.name) for f in fields(self) if f.init}
