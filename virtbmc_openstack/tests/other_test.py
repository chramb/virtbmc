from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import openstack
import pytest
from _mock_openstack import MockConnection, MockServer, mock_connect
from openstack.exceptions import ConflictException

from virtbmc_core.constants import IPMI_COMPLETION_CODES as CODE
from virtbmc_openstack import OpenStackBMC, handle_nova_exception

if TYPE_CHECKING:
    from typing import Literal

    from pytest import MonkeyPatch

    from virtbmc_openstack.types import status


def test_handle_unnknown_error() -> None:
    assert (
        handle_nova_exception(ConflictException("some other text"), ["active"])
        == CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE
    )


def test_cold_reset(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        openstack,
        "connect",
        mock_connect(MockServer()),  # type: ignore
    )
    bmc = OpenStackBMC("test", port=1028)
    th = threading.Thread(target=bmc.start, daemon=False)
    th.start()
    while not th.is_alive():
        pass
    assert bmc._stopped is False
    assert isinstance(bmc._conn, MockConnection)
    assert bmc._conn.active is True
    bmc.cold_reset()
    while th.is_alive():
        pass
    assert bmc._stopped is True
    assert bmc._conn.active is False


@pytest.mark.parametrize(
    ("status", "returns"),
    (
        ("ACTIVE", "on"),
        ("SHUTOFF", "off"),
    ),
)
def test_get_power_state(status: status, returns: Literal["on", "off"]) -> None:
    bmc = OpenStackBMC("test")
    server = MockServer(status)
    bmc._conn = MockConnection(server)  # type: ignore
    bmc._server = server  # type: ignore
    assert bmc.get_power_state() == returns


def test_power_shutdown(bmc: OpenStackBMC) -> None:
    assert bmc.power_shutdown() == CODE.SUCCESS
