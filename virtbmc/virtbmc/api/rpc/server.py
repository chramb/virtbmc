from __future__ import annotations

from multiprocessing.managers import BaseManager

import virtbmc.control as cmd


class Server(BaseManager):
    pass


Server.register("bmc_create", cmd.create)
Server.register("bmc_delete", cmd.delete)
Server.register("bmc_start", cmd.start)
Server.register("bmc_stop", cmd.stop)
Server.register("bmc_get", cmd.get)
Server.register("bmc_get_all", cmd.get_all)
