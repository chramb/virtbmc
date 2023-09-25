from __future__ import annotations

import logging
import signal
from argparse import ArgumentParser
from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING

from virtbmc.api.rpc.server import Server
from virtbmc.control import exit, init
from virtbmc_core.log import log_format

if TYPE_CHECKING:
    from typing import Any, Optional, Sequence
log = logging.getLogger("virtbmc")
log_format(log)


def main(argv: Optional[Sequence[str]] = None) -> int:
    sock = "/tmp/virtbmc.sock"
    # fmt: off
    parser = ArgumentParser("virtbmcd")
    parser.add_argument("-V", "--version", action="version", version=version("virtbmc"))
    parser.add_argument("-d","--debug", action="store_true", help="enable logging debug information to console")  # noqa: E501
    parser.add_argument("--no-autostart", action="store_true", help="don't start BMCs started on previous ran") # noqa: E501
    # fmt: off
    namespace = parser.parse_args()
    if Path(sock).exists():
        msg = (
            "ERROr: virtbmc socket already exists,"
            "this can a happen if virtbmc daemon is already running"
            "or was forcefully closed, if you're sure you want"
            f"to start the daemon please remove: '{sock}'")
        log.critical((msg))
        return -1
    server = Server(address="/tmp/virtbmc.sock", authkey=b"pass")
    if namespace.debug:
        log.setLevel(logging.DEBUG)
    if not namespace.no_autostart:
        init()
    def shutdown(sig: signal._SIGNUM, frame: Any) -> None: # noqa: ANN401
        exit()
        server.shutdown()

    signal.signal(signal.SIGINT, shutdown)
    server.get_server().serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
