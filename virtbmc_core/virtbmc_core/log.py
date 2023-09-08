from __future__ import annotations

import logging
import os
import sys

# BRIGHT_BLACK = "\33[30;1m"
# BRIGHT_RED = "\33[31;1m"
# BRIGHT_GREEN = "\33[32;1m"
# BRIGHT_YELLOW = "\33[33;1m"
# BRIGHT_BLUE = "\33[34;1m"
# BRIGHT_MAGENTA = "\33[35;1m"
# BRIGHT_CYAN = "\33[36;1m"
# BRIGHT_WHITE = "\33[37;1m"
# BLACK = "\33[30m"
RED = "\33[31m"
# GREEN = "\33[32m"
YELLOW = "\33[33m"
BLUE = "\33[34m"
# MAGENTA = "\33[35m"
# CYAN = "\33[36m"
# WHITE = "\33[37m"
RESET = "\33[0m"
BOLD = "\33[1m]"
# UNDERLINE = "\33[4m"
# REVERSED = "\33[7m"


def log_format(
    logger: logging.Logger,
    message_format: str = "{asctime} {levelname}: {message}",
    date_format: str = "%Y-%m-%d %H:%M:%S",
) -> None:
    if sys.stderr.isatty() and not os.environ.get("NO_COLOR", False):
        LEVEL_FORMAT: dict[int, str] = {
            logging.DEBUG: f"{BLUE}{message_format}{RESET}",
            logging.INFO: f"{message_format}",
            logging.WARNING: f"{YELLOW}{message_format}{RESET}",
            logging.ERROR: f"{RED}{message_format}{RESET}",
            logging.CRITICAL: f"{BOLD}{RED}{message_format}{RESET}",
        }

        class ColorFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                _format: str = LEVEL_FORMAT[record.levelno]
                _formatter = logging.Formatter(
                    fmt=_format, style="{", datefmt=date_format
                )
                return _formatter.format(record)

        formatter = ColorFormatter()
    else:
        formatter = logging.Formatter(
            fmt=message_format, style="{", datefmt=date_format
        )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
