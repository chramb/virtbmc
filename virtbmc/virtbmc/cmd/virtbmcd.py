from __future__ import annotations

import logging
from argparse import ArgumentParser
from importlib.metadata import version
from typing import TYPE_CHECKING

from virtbmc.api.rpc.server import Server
from virtbmc_core.log import log_format

if TYPE_CHECKING:
    from typing import Optional, Sequence
log = logging.getLogger("virtbmc")
log_format(log)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = ArgumentParser("virtbmcd")
    parser.add_argument("-V", "--version", action="version", version=version("virtbmc"))
    # TODO: add debug flag
    # TODO: create client -> separate package -> use schema
    parser.parse_args()
    server = Server(address="/tmp/virtbmc.sock", authkey=b"pass").get_server()

    try:
        print("server started")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
