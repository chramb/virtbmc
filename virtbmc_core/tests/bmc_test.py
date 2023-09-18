from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import pytest

from virtbmc_core.bmc import Bmc

if TYPE_CHECKING:
    from typing import Dict, Union


def test_bmc_config() -> None:
    # TODO: Add parametarize or hypothesis
    class TestBmc(Bmc):
        driver = "test"

    expected_config: Dict[str, Union[int, str, None]] = {
        "driver": TestBmc.driver,
        "username": "admin",
        "password": "password",
        "port": 623,
        "address": "::",
        "active": False,
    }
    bmc = TestBmc()
    assert bmc.config() == expected_config


def test_bmc_stop() -> None:
    bmc = Bmc()
    assert bmc._stopped is False
    bmc.stop()
    assert bmc._stopped is True


def test_bmc_start() -> None:
    bmc = Bmc(port=1025)
    t = threading.Thread(target=bmc.start, daemon=False)
    assert bmc._stopped is False
    t.start()
    assert bmc._stopped is False
    assert t.is_alive() is True
    # Cleanup
    bmc.stop()
    while t.is_alive():  # Wait for thread to stop properly
        pass


@pytest.mark.parametrize("port", (-1, 65536))
def test_invalid_port(port: int) -> None:
    with pytest.raises(ValueError):
        Bmc(port=port)


@pytest.mark.parametrize("address", ("some text",))
def test_invalid_address(address: str) -> None:
    with pytest.raises(ValueError):
        Bmc(address=address)


def test_race_condition() -> None:
    bmc = Bmc(port=1026)
    th = threading.Thread(target=bmc.start, daemon=False)
    th.start()
    bmc.stop()
