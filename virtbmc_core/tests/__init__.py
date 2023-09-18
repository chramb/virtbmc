import pytest

from virtbmc_core.bmc import Bmc


@pytest.fixture
class _TestBmc(Bmc):
    driver = "test"
