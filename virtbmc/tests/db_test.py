from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional

import pytest

from ._utils import _config, _file

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Dict

    from virtbmc.db.json import JsonDB


def _write_json(path: Path, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if config is None or config.get("name", None) is None:
        config = _config()
    with (path / f"{config['name']}.json").open("w") as f:
        json.dump(config, f)

    return config


def test_write(db: JsonDB) -> None:
    config = _write_json(db.location)
    db.write(config)
    with _file(db, config["name"]).open("r") as f:
        ret_config = json.load(f)
    assert ret_config == config


def test_write_exists(db: JsonDB) -> None:
    config = _write_json(db.location)
    db.write(config)
    db.write(config)
    with _file(db, config["name"]).open("r") as f:
        ret_config = json.load(f)
    assert ret_config == config


def test_read(db: JsonDB) -> None:
    config = _write_json(db.location)
    ret_config = db.read(config["name"])
    assert ret_config == config
    assert ret_config is not None


def test_read_not_found(db: JsonDB) -> None:
    ret_config = db.read("i don't exist")
    assert ret_config is None


def test_delete(db: JsonDB) -> None:
    config = _write_json(db.location)
    db.delete(config["name"])
    assert _file(db, config["name"]).exists() is False


def test_delete_not_exists(db: JsonDB) -> None:
    config = _config()
    with pytest.raises(expected_exception=FileNotFoundError):
        db.delete(config["name"])
    assert _file(db, config["name"]).exists() is False


def test_update_start(db: JsonDB) -> None:
    config = _write_json(db.location)
    db.update(config["name"], {"active": True})
    with _file(db, config["name"]).open("r") as f:
        assert json.load(f)["active"] is True


def test_update_stop(db: JsonDB) -> None:
    config = _write_json(db.location)
    db.update(config["name"], {"active": False})
    with _file(db, config["name"]).open("r") as f:
        assert json.load(f)["active"] is False


def test_get_active(db: JsonDB) -> None:
    (db.location / "test.ini").touch()
    for x in range(0, 10):
        _write_json(db.location, _config(str(x), active=bool(x % 2)))
    active = db.get_active()
    assert len(active) == 5
    for config in db.get_active():
        assert config["active"] is True


def test_get_active_none(db: JsonDB) -> None:
    active = db.get_active()
    assert len(active) == 0


def test_get_all(db: JsonDB) -> None:
    (db.location / "test.ini").touch()
    for x in range(0, 10):
        _write_json(db.location, _config(str(x), active=bool(x % 2)))
    all = db.get_all()
    assert len(all) == 10
    for config in db.get_active():
        assert config["active"] is True


def test_get_all_none(db: JsonDB) -> None:
    all = db.get_all()
    assert len(all) == 0
