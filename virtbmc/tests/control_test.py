from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import virtbmc.control as ctl

from ._utils import _config, _file

if TYPE_CHECKING:
    from virtbmc.db.json import JsonDB


def test_create(db: JsonDB) -> None:
    config = _config("test")
    ctl.create(config)
    assert _file(db, config["name"]).exists() is True
    assert db.read(config["name"]) == config
    assert db.read(config["name"]) is not None


def test_create_exists(db: JsonDB) -> None:
    config = _config("test")
    ctl.create(config)
    with pytest.raises(Exception):
        ctl.create(config)


def test_delete(db: JsonDB) -> None:
    config = _config("test")
    ctl.create(config)
    assert _file(db, config["name"]).exists() is True
    ctl.delete(config["name"])
    assert _file(db, config["name"]).exists() is False
    # assert _file(db, config["name"]).exists() is False


def test_delete_not_found(db: JsonDB) -> None:
    _ = db
    with pytest.raises(expected_exception=Exception):
        ctl.delete("name")


def test_start_stop(db: JsonDB) -> None:
    config = _config("test")
    name = config["name"]
    ctl.create(config)
    ctl.start(name)
    config["active"] = True
    assert ctl.get(name) == config
    ctl.stop(name)
    config["active"] = True
    assert ctl.get(name)


def test_get(db: JsonDB) -> None:
    _ = db
    config = _config("test")
    name = config["name"]
    ctl.create(config)
    assert ctl.get(name) == config


def test_get_empty(db: JsonDB) -> None:
    _ = db
    assert ctl.get_all() == ()


def test_get_all(db: JsonDB) -> None:
    _ = db
    config1 = _config("test1")
    config2 = _config("test2")
    ctl.create(config1)
    ctl.create(config2)
    assert len(ctl.get_all()) == 2
    for cfg in ctl.get_all():
        assert cfg in (config1, config2)


def test_get_all_empty(db: JsonDB) -> None:
    assert ctl.get_all() == ()


def test_delete_started(db: JsonDB) -> None:
    config = _config("test")
    name = config["name"]
    ctl.create(config)
    ctl.start(name)
    ctl.delete(name)
    assert _file(db, name).exists() is False
    assert db.read(name) is None
