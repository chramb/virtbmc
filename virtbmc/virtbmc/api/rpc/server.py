from __future__ import annotations

from multiprocessing.managers import BaseManager

import virtbmc.control as ctl


class Server(BaseManager):
    pass


Server.register("bmc_create", ctl.create)
Server.register("bmc_delete", ctl.delete)
Server.register("bmc_start", ctl.start)
Server.register("bmc_stop", ctl.stop)
