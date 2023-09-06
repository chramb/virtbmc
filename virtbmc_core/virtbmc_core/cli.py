from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import ArgumentParser, _ArgumentGroup
    from typing import Tuple


def bmc_options(parser: ArgumentParser) -> Tuple[ArgumentParser, _ArgumentGroup]:
    # fmt: off
    group = parser.add_argument_group("VirtBMC Options")
    group.add_argument("-u","--username", default="admin", type=str, action="store", help="The BMC username (default: admin)")  # noqa: E501
    group.add_argument("-P","--password", default="password", type=str, action="store", help="The BMC password (default: password)")  # noqa: E501
    group.add_argument("-p","--port", default=623, type=int, action="store", help="Port to listen on (default: 623)")  # noqa: E501
    group.add_argument("-a","--address", default="::", type=str, action="store", help="Address to listen on (default: '::')")  # noqa: E501
    # fmt: on
    return parser, group
