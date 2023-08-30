from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

try:
    import yaml
except ImportError:
    import logging
    import sys
    import textwrap

    log = logging.getLogger(__name__)

    msg = """
        Missing required dependency `PyYaml`.
        Please install it using pip or other preferred method.

        Command to install it using pip:

            $ pip install PyYaml

        """  # Switch/add virtbmc documentation if it ever gets created
    log.critical(textwrap.dedent(msg))
    sys.exit(-1)

if TYPE_CHECKING:
    from pathlib import Path


def write(config: Dict[str, Any], file: Path) -> None:
    with file.open("w") as f:
        yaml.dump(config, f)


def read(file: Path) -> Dict[str, Any]:
    with file.open("r") as f:
        return yaml.safe_load(f)
