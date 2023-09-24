from __future__ import annotations

from multiprocessing.managers import BaseManager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from virtbmc.api.rpc import _RPC

else:
    _RPC = object


# TODO: annotate wit hif TC:obj -> Protocol
class Client(BaseManager, _RPC):
    pass


Client.register("bmc_create")
Client.register("bmc_delete")
Client.register("bmc_start")
Client.register("bmc_stop")
Client.register("bmc_get")
Client.register("bmc_get_all")
