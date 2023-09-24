from __future__ import annotations

from threading import Thread
from typing import TYPE_CHECKING

from virtbmc.driver import make_bmc
from virtbmc.exception import VirtBMCError

if TYPE_CHECKING:
    from typing import Dict, Optional

    from virtbmc_core.bmc import Bmc
    from virtbmc_core.types import Config as BmcConfig


_bmc_pool: Dict[str, ThreadedBmc] = {}


def get(name: str) -> Optional[BmcConfig]:
    if tbmc := _bmc_pool.get(name, None):
        return tbmc.config()
    else:
        return None


def create(bmc_config: BmcConfig) -> None:
    # Assume config is valid and db doesn't contain given bmc["name"]
    _ = bmc_config.pop("active", None)
    bmc: Bmc = make_bmc(bmc_config)
    _bmc_pool[bmc_config["name"]] = ThreadedBmc(bmc)


def delete(name: str) -> None:
    # Assume bmc is stopped check before
    del _bmc_pool[name]


def start(name: str) -> None:
    _bmc_pool[name].start()


def stop(name: str) -> None:
    _bmc_pool[name].stop()


class ThreadedBmc:
    bmc: Bmc
    thread: Thread

    def __init__(self, bmc: Bmc) -> None:
        self.bmc = bmc
        self.thread = Thread(target=self.bmc.start)
        self._started: bool = False

    def start(self) -> None:
        if self._started:
            raise VirtBMCError("bmc already started")
        self._started = True
        self.thread.start()

    def stop(self) -> None:
        if self._started is False:
            raise VirtBMCError("bmc already stopped")

        self._started = False
        self.bmc.stop()

    def config(self) -> BmcConfig:
        config = self.bmc.config()
        return config
