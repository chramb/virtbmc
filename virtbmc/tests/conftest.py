from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from virtbmc.db.json import JsonDB

# isort: off
from ._utils import _TestBMC
import virtbmc.driver

virtbmc.driver.driver = {"testing": _TestBMC}  # Mock available drivers

import virtbmc.control as ctl  # noqa: E402

# isort: on


if TYPE_CHECKING:
    from pathlib import Path
    from typing import Generator


@pytest.fixture(scope="function")
def db(tmp_path: Path) -> Generator[JsonDB, None, None]:
    ctl.db = JsonDB(tmp_path)
    yield ctl.db
