from __future__ import annotations

from multiprocessing.managers import BaseManager
from typing import TYPE_CHECKING

import virtbmc.control as ctl

if TYPE_CHECKING:
    from typing import Optional, Tuple

    from virtbmc.api.rpc import _RPC
    from virtbmc_core.types import Config as BmcConfig

else:
    _RPC = object


# TODO: annotate wit hif TC:obj -> Protocol
class Client(BaseManager, _RPC):
    def bmc_get(self, name: str) -> Optional[BmcConfig]:
        return ctl.get(name)

    def bmc_get_all(self) -> Tuple[BmcConfig, ...]:
        return ctl.get_all()


Client.register("bmc_create")
Client.register("bmc_delete")
Client.register("bmc_start")
Client.register("bmc_stop")
