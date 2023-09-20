from __future__ import annotations

from threading import Thread
from typing import TYPE_CHECKING

from virtbmc.driver import driver

if TYPE_CHECKING:
    from typing import Dict

    from virtbmc.manager import Manager
    from virtbmc_core.bmc import Bmc
    from virtbmc_core.types import Config as BmcConfig
else:
    Manager = object


class ThreadingManager(Manager):
    def __init__(self) -> None:
        self._bmc_pool: Dict[str, ThreadedBmc] = {}

    def create(self, bmc_config: BmcConfig) -> None:
        # Assume config is valid and db doesn't contain given bmc["name"]
        _ = bmc_config.pop("active")
        bmc: Bmc = driver[bmc_config.pop("driver")](**bmc_config)  # type: ignore
        self._bmc_pool[bmc_config["name"]] = ThreadedBmc(bmc)
        ...

    def delete(self, name: str) -> None:
        # Assume bmc is stopped check before
        del self._bmc_pool["name"]

    def start(self, name: str) -> None:
        self._bmc_pool[name].start()

    def stop(self, name: str) -> None:
        self._bmc_pool[name].stop()


class ThreadedBmc:
    bmc: Bmc
    thread: Thread
    _started: bool  # TODO: remove _started use bmc.active instead

    def __init__(self, bmc: Bmc) -> None:
        self.bmc = bmc
        self.thread = Thread(target=self.bmc.start)

    def start(self) -> None:
        if self.bmc.active:
            raise Exception("bmc already started")  # FIXME custom exception
        else:
            self.thread = Thread(target=self.bmc.start)

        self.thread.start()

    def stop(self) -> None:
        if self.bmc.active is False:
            raise Exception("already off")

        self.bmc.stop()
