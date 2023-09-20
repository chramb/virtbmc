from __future__ import annotations

from multiprocessing.managers import BaseManager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple

    from virtbmc_core.types import Config as BmcConfig

    class _Client:
        # fmt: off
        def bmc_create(self, bmc_config: BmcConfig) -> None:...
        def bmc_delete(self, name: str) -> None:...
        def bmc_start(self, name: str) -> None:...
        def bmc_stop(self, name: str) -> None:...
        def bmc_get(self, name: str) -> BmcConfig:...
        def bmc_get_all(self) -> Tuple[BmcConfig,...]:...
        # fmt: on

else:
    _Client = object


# TODO: annotate wit hif TC:obj -> Protocol
class Client(BaseManager, _Client):
    pass


Client.register("bmc_create")
Client.register("bmc_delete")
Client.register("bmc_start")
Client.register("bmc_stop")
Client.register("bmc_get")
Client.register("bmc_get_all")
