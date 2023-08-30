from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseBMC

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Union
check_optional_deps: Dict[str, List[str]] = {
    "dummy": ["virtbmc"],
    "openstack": ["openstack"],
}
