import pytest
from pyghmi.ipmi.private.constants import ipmi_completion_codes

from virtbmc_core.constants import IPMI_COMPLETION_CODES


@pytest.mark.parametrize(
    "code",
    (x for x in ipmi_completion_codes),
    ids=(y for y in ipmi_completion_codes.values()),
)
def test_completion_codes(code: int) -> None:
    "Test whether codes included in pyghmi are part of IPMI_COMPLETION_CODES"
    assert (
        ipmi_completion_codes[code].upper().replace(" ", "_").replace(",", "")
        == IPMI_COMPLETION_CODES(code).name
    )
