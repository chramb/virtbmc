from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from _mock_openstack import MockConnection, MockServer

from virtbmc_core.constants import IPMI_COMPLETION_CODES as CODE
from virtbmc_openstack import OpenStackBMC

if TYPE_CHECKING:
    from typing import Optional, Tuple

    from virtbmc_openstack.types import status, task_state, vm_state

OK = int(CODE.SUCCESS)
ERR = int(CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE)

states: Tuple[Tuple[status, vm_state, Optional[task_state], bool], ...] = (
    # idle on
    ("ACTIVE", "active", None, True),
    # idle off
    ("SHUTOFF", "stopped", None, False),
    # powering-on
    ("SHUTOFF", "stopped", "powering-on", True),
    # powering-off
    ("ACTIVE", "active", "powering-off", False),
    # reboot-soft
    ("REBOOT", "active", "reboot_pending", False),
    ("REBOOT", "active", "reboot_started", False),
    ("REBOOT", "active", "rebooting", False),
    # reboot-hard
    ("ACTIVE", "active", "reboot_pending_hard", False),
    ("ACTIVE", "active", "reboot_started_hard", False),
    ("ACTIVE", "active", "rebooting_hard", False),
)


@pytest.mark.parametrize("bmc_stopped", (True, False))
@pytest.mark.parametrize(("status", "vm_state", "task_state", "is_active"), states)
def test_is_active(
    status: status,
    vm_state: vm_state,
    task_state: task_state,
    is_active: bool,
    bmc_stopped: bool,
) -> None:
    bmc = OpenStackBMC("test")
    server = MockServer(status, vm_state, task_state)
    bmc._conn = MockConnection(server)  # type: ignore
    bmc._server = server  # type: ignore
    bmc._stopped = bmc_stopped
    assert bmc.is_active() == is_active


def test_is_active_no_server() -> None:
    bmc = OpenStackBMC("test")
    bmc._conn = MockConnection(None)  # type: ignore
    bmc._server = None  # type: ignore
    assert bmc.is_active() is False
