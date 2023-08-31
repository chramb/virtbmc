from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

import pyghmi.ipmi.bmc as _bmc
import pyghmi.ipmi.private.session as _ipmisession

if TYPE_CHECKING:
    from typing import TypedDict

    class BmcConfig(TypedDict):
        name: str
        driver: str
        username: str
        password: str
        port: int
        address: str


@dataclass
class Bmc(_bmc.Bmc):  # type: ignore[misc]
    name: str
    driver: str = field(init=False, default="None")
    username: str = "admin"
    password: str = "password"
    port: int = 623
    address: str = "::"
    _started: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        super().__init__(
            authdata={self.username: self.password},
            address=self.address,
            port=self.port,
        )

    def listen(self, timeout: int = 30) -> None:  # type: ignore[override]
        self._started = True
        while self._started:
            _ipmisession.Session.wait_for_rsp(timeout)

    def stop(self) -> None:
        self._started = False

    def config(self) -> BmcConfig:
        # fmt: off
        return {f.name: getattr(self, f.name) for f in fields(self) if f.repr} # type: ignore[return-value]
        # fmt: on
