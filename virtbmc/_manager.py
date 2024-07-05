from __future__ import annotations

import logging
from threading import Lock, Thread
from typing import TYPE_CHECKING

import virtbmc._db as db
from virtbmc.driver import Bmc
from virtbmc.exception import VirtBmcFailedToStart, VirtBmcFailedToStop, VirtBmcNotFound

if TYPE_CHECKING:
    from typing import Sequence, Unpack

    from virtbmc.core import Bmc as BaseBmc
    from virtbmc.core.types import BmcConfig

_bmc_pool: dict[str, ThreadedBmc] = {}

log = logging.getLogger("virtbmc.manager")


def init() -> None:
    db.init()
    for bmc in db.list():
        create(**bmc)
        if bmc["properties"].get("active"):
            log.debug(f"starting previously activated BMC: {bmc["driver"]}:{bmc["name"]}")
            start(bmc["name"], ignore_db=True)


def exit() -> None:
    for name, bmc in _bmc_pool.items():
        db.update(name, bmc.config())
        bmc.stop()
    _bmc_pool.clear()


def create(**bmc_config: Unpack[BmcConfig]) -> None:
    # Assume config is valid and db doesn't contain given bmc["name"]
    # TODO: validate if bmc with same socket binding doesn't exist
    bmc = Bmc(**bmc_config)
    _bmc_pool[bmc_config["name"]] = ThreadedBmc(bmc)
    db.create(**bmc_config)


def delete(name: str) -> None:
    # Assume bmc is stopped check before
    del _bmc_pool[name]
    db.delete(name)


def start(name: str, ignore_db: bool = False) -> None:
    bmc = _bmc_pool.get(name)
    if bmc is None:
        msg = f"{name} not found among created Bmcs"
        raise VirtBmcNotFound(msg)
    try:
        bmc.start()
        db.start(name)
    except OSError as e:
        raise VirtBmcFailedToStart(e.strerror)
    except Exception as e:
        log.exception(e)
        raise VirtBmcFailedToStart(str(e))


def stop(name: str) -> None:
    db.stop(name)
    _bmc_pool[name].stop()


def list(only_active: bool = False) -> Sequence[BmcConfig]:
    return db.list(only_active)


def show(name: str) -> BmcConfig | None:
    return db.show(name)


class ThreadedBmc:
    bmc: BaseBmc
    thread: Thread
    lock: Lock

    def __init__(self, bmc: BaseBmc, timeout: int = 30) -> None:
        self.bmc = bmc
        self.thread = Thread(target=self.bmc.start, args=(timeout,), daemon=False)
        self.lock = Lock()
        self.timeout = timeout

    def start(self) -> None:
        with self.lock:
            if self.thread.is_alive():
                msg = "bmc already running"
                raise VirtBmcFailedToStart(msg)
            self.thread.start()

    def stop(self) -> None:
        with self.lock:
            if not self.thread.is_alive():
                msg = "bmc already stopped"
                raise VirtBmcFailedToStop(msg)

            self.bmc.stop()
            self.thread = Thread(target=self.bmc.start, args=(self.timeout,), daemon=False)

    def config(self) -> BmcConfig:
        with self.lock:
            config = self.bmc.config()
            return {**config, "active": self.thread.is_alive()}  # type: ignore
