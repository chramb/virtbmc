from __future__ import annotations

import threading
from argparse import ArgumentParser, Namespace
from typing import TYPE_CHECKING

import openstack
from ._mock_openstack import MockConnection, MockServer, mock_connect

from virtbmc_openstack import OpenStackBMC

if TYPE_CHECKING:
    from pytest import MonkeyPatch


def test_create() -> None:
    bmc = OpenStackBMC(name="test")
    assert bmc.config() == {
        "driver": "openstack",
        "cloud": None,
        "name": "test",
        "username": "admin",
        "password": "password",
        "port": 623,
        "address": "::",
    }


def test_start_stop(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        openstack,
        "connect",
        mock_connect(MockServer("ACTIVE")),
    )
    bmc = OpenStackBMC(name="test", port=1027)
    t = threading.Thread(target=bmc.start, daemon=False)
    t.start()
    while not t.is_alive():
        pass
    assert isinstance(bmc._conn, MockConnection)
    assert bmc._conn.active is True
    bmc.stop()
    assert bmc._conn.active is False
    while t.is_alive():
        pass


# TODO: failed to connect test
def test_server_not_found(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        openstack,
        "connect",
        mock_connect(None),  # type: ignore
    )
    bmc = OpenStackBMC(name="test", port=1027)
    t = threading.Thread(target=bmc.start, daemon=False)
    t.start()
    while t.is_alive():
        pass
    assert bmc._stopped is True


def test_cli() -> None:
    ap = ArgumentParser(prog="test")
    OpenStackBMC.cli(ap)
    parsed = ap.parse_args("--os-cloud y x".split())
    assert parsed.server == "x"
    assert parsed.os_cloud == "y"


def test_cli_woosc() -> None:
    ap = ArgumentParser(prog="test")
    OpenStackBMC.cli(ap, os_cloud=False)
    parsed = ap.parse_args("x")
    assert parsed.server == "x"


def test_from_namespace() -> None:
    bmc = OpenStackBMC("test")
    ns = Namespace(**bmc.config(), server=bmc.config()["name"], os_cloud=None)
    bmc2 = OpenStackBMC.from_namespace(ns)
    assert bmc.config() == bmc2.config()
