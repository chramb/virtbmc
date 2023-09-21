from __future__ import annotations

import pytest
from pyghmi.ipmi.command import boot_devices
from pyghmi.ipmi.private.constants import ipmi_completion_codes

from virtbmc_core.constants import BOOT_DEVICES, IPMI_COMPLETION_CODES


@pytest.mark.parametrize(
    "code",
    (x for x in ipmi_completion_codes),
    ids=(y for y in ipmi_completion_codes.values()),
)
def test_completion_codes(code: int) -> None:
    "Test whether codes included in pyghmi map correctly to IPMI_COMPLETION_CODES"
    assert (
        ipmi_completion_codes[code].upper().replace(" ", "_").replace(",", "")
        == IPMI_COMPLETION_CODES(code).name
    )


@pytest.mark.parametrize("device", (x for x in boot_devices if isinstance(x, str)))
def test_boot_devices(device: str) -> None:
    "Test whether boot devices included in pyghmi map to correct BOOT_DEVICES constant"
    assert boot_devices[device] == BOOT_DEVICES(boot_devices[device])
