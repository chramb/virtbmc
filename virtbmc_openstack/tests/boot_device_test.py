from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Literal

    from virtbmc_openstack import OpenStackBMC


def test_get_bood_device(bmc: OpenStackBMC) -> None:
    bmc._server.metadata = {"libvirt:pxe-first": ""}
    assert bmc.get_boot_device() == "hd"


def test_get_bood_device_unser(bmc: OpenStackBMC) -> None:
    assert bmc.get_boot_device() == "hd"


def test_get_bood_device_net(bmc: OpenStackBMC) -> None:
    bmc._server.metadata = {"libvirt:pxe-first": "1"}
    assert bmc.get_boot_device() == "network"


@pytest.mark.parametrize("device", ("network", "hd"))
def test_set_boot_device(bmc: OpenStackBMC, device: Literal["network", "hd"]) -> None:
    bmc.set_boot_device(device)
    assert bmc._server.metadata == {
        "libvirt:pxe-first": "1" if device == "network" else ""
    }


def test_set_boot_device_errors(bmc: OpenStackBMC) -> None:
    bmc.set_boot_device("cd")
    assert bmc._server.metadata == {}
