from __future__ import annotations

from typing import TYPE_CHECKING

from virtbmc_core.log import log_configure
from virtbmc_core.config.get_config import CONFIG
from virtbmc_core.config.serialize import read, write

if TYPE_CHECKING:
    from virtbmc_core.model.app_config import AppConfig
    from typing import List

__all__: List[str] = ["CONFIG", "read", "write"]

log_configure(CONFIG)
