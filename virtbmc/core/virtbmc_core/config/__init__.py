from __future__ import annotations

from typing import TYPE_CHECKING

from virtbmc_core.log import log_configure
from virtbmc_core.config.get import get_config
from virtbmc_core.config.serialize import read, write

if TYPE_CHECKING:
    from virtbmc_core.model import AppConfig
    from typing import List

__all__: List[str] = ["CONFIG", "read", "write"]

CONFIG: AppConfig = get_config()
log_configure(CONFIG)
