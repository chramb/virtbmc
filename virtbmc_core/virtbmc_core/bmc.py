from __future__ import annotations

from typing import TYPE_CHECKING

import pyghmi.ipmi.bmc as _bmc
import pyghmi.ipmi.private.session as _ipmisession

if TYPE_CHECKING:
    from typing import TypedDict

    class BmcConfig(TypedDict):
        driver: str
        name: str
        username: str
        password: str
        port: int
        address: str


class Bmc(_bmc.Bmc):
    driver: str
    _stopped: bool = False

    def __init__(
        self,
        name: str,
        username: str = "admin",
        password: str = "password",
        port: int = 623,
        address: str = "::",
    ) -> None:
        self.name = name
        self.username = username
        self.password = password
        self.port = port
        self.address = address

    def start(self, timeout: int = 30) -> None:
        super().__init__(
            authdata={self.username: self.password},
            address=self.address,
            port=self.port,
        )

        while not self._stopped:
            _ipmisession.Session.wait_for_rsp(timeout)

    def stop(self) -> None:
        self._stopped = True

    def config(self) -> BmcConfig:
        # This is incorrect return statement for children classes
        # but more helpful than the proper one
        return {"driver": self.driver, **vars(self)}  # type: ignore[misc]
