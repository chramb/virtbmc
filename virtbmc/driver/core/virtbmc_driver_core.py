from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, Optional

from pyghmi.ipmi.bmc import Bmc, ipmisession

try:
    from virtbmc.config import CONFIG  # pyright: ignore[reportMissingImports]

    session_timeout: int = CONFIG.ipmi.session_timeout
except ImportError:
    session_timeout = 1

if TYPE_CHECKING:
    from typing import Any, Dict, TypedDict

    class BmcConfig(TypedDict):
        name: str
        driver: str
        username: str
        password: str
        port: int
        address: str
        autostart: bool


@dataclass
class BMC(Bmc):
    name: str
    driver: str = field(init=False)  # Fancy way to create "ABC" ^1
    username: str = "admin"
    password: str = "password"
    port: int = 6230
    address: str = "::1"
    bmcuuid: Optional[str] = field(default=None, repr=False)
    _started: bool = field(default=False, init=False, repr=False)
    # *^1: explanation
    # this class doesn't have driver in __init__ method but requires it to be initialized,
    # therefore no way of creating it without inheriting from it

    def __post_init__(self) -> None:
        super().__init__(
            {self.username: self.password}, self.port, self.bmcuuid, self.address
        )

    def listen(self) -> None:
        self._started = True
        while self._started:
            ipmisession.Session.wait_for_rsp(session_timeout)

    def stop(self) -> None:
        self._started = False

    def config(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.repr}
