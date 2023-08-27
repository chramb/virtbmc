from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from virtbmc.config import AppConfig


# TODO(logging): to file, single file, config colors
def log_configure(config: AppConfig):
    _a = ANSI_COLORS = {  # noqa F831
        "BRIGHT_BLACK": "\33[30;1m",
        "BRIGHT_RED": "\33[31;1m",
        "BRIGHT_GREEN": "\33[32;1m",
        "BRIGHT_YELLOW": "\33[33;1m",
        "BRIGHT_BLUE": "\33[34;1m",
        "BRIGHT_MAGENTA": "\33[35;1m",
        "BRIGHT_CYAN": "\33[36;1m",
        "BRIGHT_WHITE": "\33[37;1m",
        "BLACK": "\33[30m",
        "RED": "\33[31m",
        "GREEN": "\33[32m",
        "YELLOW": "\33[33m",
        "BLUE": "\33[34m",
        "MAGENTA": "\33[35m",
        "CYAN": "\33[36m",
        "WHITE": "\33[37m",
        "RESET": "\33[0m",
        "BOLD": "\33[1m]",
        "UNDERLINE": "\33[4m",
        "REVERSED": "\33[7m",
    }
    FORMAT = config.log.format

    LEVEL_FORMAT = {
        logging.DEBUG: f"{_a['BLUE']}{FORMAT}{_a['RESET']}",
        logging.INFO: f"{FORMAT}",
        logging.WARNING: f"{_a['YELLOW']}{FORMAT}{_a['RESET']}",
        logging.ERROR: f"{_a['RED']}{FORMAT}{_a['RESET']}",
        logging.CRITICAL: f"{_a['BOLD']}{_a['RED']}{FORMAT}{_a['RESET']}",
    }

    class ColorFormatter(logging.Formatter):
        def format(self, record):
            _format = LEVEL_FORMAT[record.levelno]
            _formatter = logging.Formatter(_format, style="{")
            return _formatter.format(record)

    log = logging.getLogger("virtbmc")
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter())
    log.addHandler(handler)
    log.setLevel(level=logging.DEBUG if config.log.debug else logging.INFO)


# def log_name(__name__: str = "virtbmc") -> str:
#     p = __name__.split(".")
#     return p[0].replace("_", ".") + ".".join(p[1:])
