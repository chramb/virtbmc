"""Module responsible for managing all BMCs."""
# ruff: noqa: ANN401
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Protocol

    from virtbmc_core.types import Config as BmcConfig

    # fmt: off
    class Manager(Protocol):
        def create(self, bmc_config: BmcConfig) -> None:...
        def delete(self, name: str) -> None:...
        def start(self, name: str) -> None:...
        def stop(self, name: str) -> None:...
    # fmt: on
