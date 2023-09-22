# ruff: noqa: ANN401
from __future__ import annotations

import time
from typing import TYPE_CHECKING

from openstack.exceptions import ConflictException, ResourceNotFound

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Literal, Optional

    from openstack.compute.v2.server import Server

    from virtbmc_openstack.types import status, task_state, vm_state


def build_exception(
    task: Literal["start", "stop", "reboot"], server: MockServer
) -> ConflictException:
    action = "task_state" if server.task_state else "vm_state"
    return ConflictException(
        message="ConflictException 409",
        http_status=409,
        details=(
            "Client Error for url: /v2.1/servers/<id>/action, "
            f"Cannot {task} instance <id> while it is in "
            f"{action} {server.task_state or server.vm_state}"
        ),
    )


def mock_connect(server: MockServer) -> Callable[[Optional[str]], MockConnection]:
    def connect(cloud: Optional[str]) -> MockConnection:
        return MockConnection(server)

    return connect


class MockCompute:
    def __init__(self, server: MockServer) -> None:
        self.mock_server: MockServer = server

    def find_server(self, name_or_id: str) -> MockServer:
        return self.mock_server

    def get_server(self, server: MockServer) -> MockServer:
        return self.mock_server

    def start_server(self, server: Server) -> None:
        raise NotImplementedError

    def stop_server(self, server: Server) -> None:
        raise NotImplementedError

    def reboot_server(
        self, server: Server, reboot_type: Literal["HARD", "SOFT"]
    ) -> None:
        raise NotImplementedError


class MockConnection:
    def __init__(self, server: MockServer) -> None:
        self.compute = MockCompute(server)
        self.active = True

    def close(self) -> None:
        self.active = False
        pass


class MockServer:
    def __init__(
        self,
        status: status = "ACTIVE",
        vm_state: vm_state = "active",
        task_state: Optional[task_state] = None,
        request_delay: float = 0,
    ) -> None:
        self.status = status
        self.vm_state = vm_state
        self.task_state = task_state
        self.metadata: Dict[str, Any] = {}
        self.delay: float = request_delay

    def __repr__(self) -> str:
        return (
            "MockServer("
            f"status={self.status},"
            f"task_state={self.task_state},"
            f"delay={self.delay}"
            ")"
        )

    def stop(self, session: Any) -> None:
        time.sleep(self.delay)
        if self.status == "ACTIVE" and self.task_state is None:
            self.status = "SHUTOFF"
            return
        else:
            raise build_exception("stop", self)

    def start(self, session: Any) -> None:
        time.sleep(self.delay)
        if self.status == "SHUTOFF" and self.task_state is None:
            self.status = "ACTIVE"
            return
        else:
            raise build_exception("start", self)

    def reboot(self, session: Any, reboot_type: Literal["SOFT", "HARD"]) -> None:
        time.sleep(self.delay)
        if self.status == "ACTIVE" and self.task_state is None:
            return
        else:
            raise build_exception("reboot", self)

    def get_metadata_item(self, session: Any, key: str) -> "MockServer":
        try:
            self.metadata[key]
            return self
        except KeyError:
            raise ResourceNotFound(
                "Metadata item does not exist: "
                f"Client Error for url: /v2.1/servers/<id>/metadata/{key}, "
                "Metadata item was not found"
            )

    def set_metadata_item(self, session: Any, key: str, value: str) -> None:
        self.metadata[key] = value
