from __future__ import annotations

import importlib.metadata
import logging
from typing import TYPE_CHECKING

from virtbmc.exception import VirtBmcDriverError

if TYPE_CHECKING:
    from typing import Any, Type

    from virtbmc.core import Bmc as _Bmc

    EPs = importlib.metadata.EntryPoints

log = logging.getLogger("virtbmc.driver")

_eps: EPs = importlib.metadata.entry_points()


def get_drivers() -> dict[str, Type[_Bmc]]:
    drivers: dict[str, Any] = {}
    for ep in _eps:
        if ep.group == "virtbmc.driver":
            try:
                drivers[ep.name] = ep.load()
                log.debug(f"successfully loaded '{ep.name}' driver")
            except Exception as e:
                log.debug(e)
    return drivers


_driver: dict[str, Type[_Bmc]] = get_drivers()


class Bmc:
    def __new__(cls, /, driver: str, **kwargs: Any) -> _Bmc:
        try:
            return _driver[driver](**kwargs)
        except KeyError:
            msg = f"driver with name {driver} not available in {_driver.keys()}"
            log.exception(msg)
            raise VirtBmcDriverError(msg)
        except Exception as e:
            log.exception(e)
            raise VirtBmcDriverError(str(e)) from e
