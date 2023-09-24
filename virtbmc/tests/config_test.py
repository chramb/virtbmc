from __future__ import annotations

import os
from typing import TYPE_CHECKING

import virtbmc.config as cfg

if TYPE_CHECKING:
    from pathlib import Path


def test_path(tmp_path: Path) -> None:
    cfg._VALID_PATHS = (str(tmp_path),)
    assert cfg.get_config_location() == tmp_path


def test_path_env(tmp_path: Path) -> None:
    os.environ["VIRTBMC_CONFIG"] = str(tmp_path)
    assert cfg.get_config_location() == tmp_path
