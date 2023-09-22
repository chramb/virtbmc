from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from _mock_openstack import MockConnection, MockServer

from virtbmc_openstack import OpenStackBMC

if TYPE_CHECKING:
    from typing import Generator


@pytest.fixture(scope="function")
def bmc() -> Generator[OpenStackBMC, None, None]:
    bmc = OpenStackBMC("test")
    server = MockServer()
    bmc._conn = MockConnection(server)  # type: ignore
    bmc._server = server  # type: ignore
    yield bmc
