from __future__ import annotations

import functools
import threading
from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, Optional

from pyghmi.ipmi.bmc import Bmc, ipmisession
from virtbmc.config import CONFIG

if TYPE_CHECKING:
    from typing import TypedDict

    class BmcConfig(TypedDict):
        name: str
        driver: str
        username: str
        password: str
        port: int
        address: str
        autostart: bool


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


@dataclass
@_handle_not_implemented_methods
class BaseBMC(Bmc):
    name: str
    driver: str = field(init=False)  # Fancy way to create "ABC" ^1
    username: str = "admin"
    password: str = "password"
    port: int = 6230
    address: str = "::1"
    autostart: bool = False
    bmcuuid: Optional[str] = field(default=None, repr=False)
    thread: threading.Thread = field(init=False, repr=False)
    started: bool = field(default=False, init=False, repr=False)
    # *^1: explanation
    # this class doesn't have driver in __init__ method but requires it to be initialized,
    # therefore no way of creating it without inheriting from it

    def __post_init__(self) -> None:
        super().__init__(
            {self.username: self.password}, self.port, self.bmcuuid, self.address
        )
        self.thread = threading.Thread(target=self.listen, daemon=False)

    def listen(self) -> None:
        self.started = True
        while self.started:
            ipmisession.Session.wait_for_rsp(CONFIG.ipmi.session_timeout)

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.started = False

    def config(self) -> BmcConfig:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.repr} # type: ignore
