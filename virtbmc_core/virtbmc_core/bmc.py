from __future__ import annotations

from typing import TYPE_CHECKING

import pyghmi.ipmi.bmc as _bmc
import pyghmi.ipmi.private.session as _ipmisession

if TYPE_CHECKING:
    from virtbmc_core.types import Config


class Bmc(_bmc.Bmc):
    driver: str
    _stopped: bool = False

    def __init__(
        self,
        username: str = "admin",
        password: str = "password",
        port: int = 623,
        address: str = "::",
    ) -> None:
        self.username = username
        self.password = password
        self.port = port
        if port < 0 or port > 65535:
            raise ValueError("Invalid port number")
        self.address = address

    def start(self, timeout: int = 30) -> None:
        super().__init__(
            authdata={self.username: self.password},
            address=self.address,
            port=self.port,
        )

        while not self._stopped:
            _ipmisession.Session.wait_for_rsp(timeout)  # pragma: no cover

    def stop(self) -> None:
        self._stopped = True

    def config(self) -> Config:
        return {
            "driver": getattr(self, "driver", None),
            **{k: v for k, v in vars(self).items() if not k.startswith("_")},
        }
