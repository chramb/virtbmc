from __future__ import annotations


class VirtBMCError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(msg)
