from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from ._mock_openstack import MockConnection, MockServer

from virtbmc_core.constants import IPMI_COMPLETION_CODES as CODE
from virtbmc_openstack import OpenStackBMC

if TYPE_CHECKING:
    from typing import Optional, Tuple

    from virtbmc_openstack.types import status, task_state, vm_state

OK = int(CODE.SUCCESS)
ERR = int(CODE.COMMAND_NOT_SUPPORTED_IN_PRESENT_STATE)

states: Tuple[Tuple[status, vm_state, Optional[task_state], int], ...] = (
    # idle on
    ("ACTIVE", "active", None, OK),
    # idle off
    ("SHUTOFF", "stopped", None, OK),
    # powering-on
    ("SHUTOFF", "stopped", "powering-on", OK),
    # powering-off
    ("ACTIVE", "active", "powering-off", ERR),
    # reboot-soft
    ("REBOOT", "active", "reboot_pending", ERR),
    ("REBOOT", "active", "reboot_started", ERR),
    ("REBOOT", "active", "rebooting", ERR),
    # reboot-hard
    ("ACTIVE", "active", "reboot_pending_hard", ERR),
    ("ACTIVE", "active", "reboot_started_hard", ERR),
    ("ACTIVE", "active", "rebooting_hard", ERR),
)


@pytest.mark.parametrize(("status", "vm_state", "task_state", "result"), states)
def test_power_on(
    status: status, vm_state: vm_state, task_state: task_state, result: CODE
) -> None:
    bmc = OpenStackBMC("test")
    server = MockServer(status, vm_state, task_state)
    bmc._conn = MockConnection(server)  # type: ignore
    bmc._server = server  # type: ignore
    assert bmc.power_on() == result
