from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

# NOTE: virtbmc.driver.driver is patched in conftest.py to include _TestBMC
import virtbmc.manager.threading as tmgr
from virtbmc.exception import VirtBMCError

from ._utils import _config, _TestBMC

if TYPE_CHECKING:
    from typing import Generator

    ThreadedBmc = tmgr.ThreadedBmc


@pytest.fixture
def mktbmc() -> Generator[str, None, None]:
    name: str = "test"
    tmgr._bmc_pool[name] = tmgr.ThreadedBmc(_TestBMC(name=name))  # type: ignore
    yield name
    tmgr._bmc_pool = {}


def test_get_none() -> None:
    result = tmgr.get("test")
    assert result is None


def test_get(mktbmc: str) -> None:
    result = tmgr.get(mktbmc)
    assert result is not None


def test_create() -> None:
    config = _config(name="test", driver="testing")
    tmgr.create(config)
    assert (tmgr._bmc_pool["test"].config()) == _config(name="test", driver="testing")


def test_delete(mktbmc: str) -> None:
    tmgr.delete(mktbmc)
    assert tmgr._bmc_pool == {}


def test_start_stop(mktbmc: str) -> None:
    tmgr.start(mktbmc)
    assert tmgr._bmc_pool[mktbmc].config()["active"] is True
    tmgr.stop(mktbmc)
    assert tmgr._bmc_pool[mktbmc].config()["active"] is False


def test_start_already_on(mktbmc: str) -> None:
    tmgr.start(mktbmc)
    assert tmgr._bmc_pool[mktbmc].config()["active"] is True
    with pytest.raises(VirtBMCError):
        tmgr.start(mktbmc)
    tmgr.stop(mktbmc)


def test_stop_already_off(mktbmc: str) -> None:
    with pytest.raises(VirtBMCError):
        tmgr.stop(mktbmc)
