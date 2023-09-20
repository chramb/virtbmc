from __future__ import annotations

from ipaddress import ip_address
from typing import TYPE_CHECKING

import pyghmi.ipmi.bmc as _bmc
import pyghmi.ipmi.private.session as _ipmisession

if TYPE_CHECKING:
    from argparse import Namespace, _ActionsContainer
    from typing import TypeVar

    from virtbmc_core.types import Config

    ActionsContainer = TypeVar("ActionsContainer", bound=_ActionsContainer)


class Bmc(_bmc.Bmc):
    driver: str

    def __init__(
        self,
        username: str = "admin",
        password: str = "password",
        port: int = 623,
        address: str = "::",
    ) -> None:
        self._stopped: bool = False
        self.active: bool = False
        self.username = username
        self.password = password
        self.active = False

        if port < 0 or port > 65535:
            raise ValueError("Invalid value in the port field")
        self.port = port

        try:
            self.address = str(ip_address(address))
        except ValueError:
            raise ValueError("Invalid value in the ip address field")

    def start(self, timeout: int = 30) -> None:
        self.active = True
        super().__init__(
            authdata={self.username: self.password},
            address=self.address,
            port=self.port,
        )

        while not self._stopped:
            _ipmisession.Session.wait_for_rsp(timeout)  # pragma: no cover

    def stop(self) -> None:
        self.active = False
        self._stopped = True

    def config(self) -> Config:
        return {
            "driver": getattr(self, "driver", None),
            **{k: v for k, v in vars(self).items() if not k.startswith("_")},
        }

    @staticmethod
    def cli(parser: ActionsContainer) -> ActionsContainer:
        # fmt: off
        parser.add_argument("-u","--username", default="admin", type=str, action="store", help="The BMC username (default: admin)")  # noqa: E501
        parser.add_argument("-P","--password", default="password", type=str, action="store", help="The BMC password (default: password)")  # noqa: E501
        parser.add_argument("-p","--port", default=623, type=int, action="store", help="Port to listen on (default: 623)")  # noqa: E501
        parser.add_argument("-a","--address", default="::", type=str, action="store", help="Address to listen on (default: '::')")  # noqa: E501
        # fmt: on
        return parser

    @staticmethod
    def from_namespace(namespace: Namespace) -> Bmc:
        raise NotImplementedError
