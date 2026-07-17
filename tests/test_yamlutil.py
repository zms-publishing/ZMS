import time
import builtins
import pytest
from unittest.mock import patch, MagicMock
from Products.zms import yamlutil


# ---------------------------------------------------------
# _load_yaml
# ---------------------------------------------------------

def test_load_yaml_success():
    with patch("yamlutil._load_yaml.__globals__['ruamel']") as ruamel:
        YAML = MagicMock()
        ruamel.yaml = MagicMock(YAML=YAML)
        result, err = yamlutil._load_yaml()
        assert result is YAML
        assert err is None


def test_load_yaml_import_error():
    with patch("ruamel.yaml", side_effect=ImportError):
        result, err = yamlutil._load_yaml()
        assert result is None
        assert err == yamlutil.IMPORT_ERROR_MSG


# ---------------------------------------------------------
# dump()
# ---------------------------------------------------------

def test_dump_import_error():
    with patch("yamlutil._load_yaml", return_value=(None, yamlutil.IMPORT_ERROR_MSG)):
        assert yamlutil.dump({"a": 1}) == yamlutil.IMPORT_ERROR_MSG


def test_dump_struct_time_serialization():
    YAML = MagicMock()
    yaml_instance = MagicMock()
    YAML.return_value = yaml_instance

    with patch("yamlutil._load_yaml", return_value=(YAML, None)):
        stream = MagicMock()
        yaml_instance.dump = MagicMock()

        data = time.strptime("2024-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")
        yamlutil.dump({"t": data})

        # Representer should be registered
        assert yaml_instance.representer.add_representer.called

        # Dump should be called
        assert yaml_instance.dump.called


def test_dump_error_during_serialization():
    YAML = MagicMock()
    yaml_instance = MagicMock()
    YAML.return_value = yaml_instance

    yaml_instance.dump.side_effect = Exception("boom")

    with patch("yamlutil._load_yaml", return_value=(YAML, None)):
        result = yamlutil.dump({"a": 1})
        assert "Error during YAML serialization" in result


# ---------------------------------------------------------
# parse()
# ---------------------------------------------------------

def test_parse_import_error():
    with patch("yamlutil._load_yaml", return_value=(None, yamlutil.IMPORT_ERROR_MSG)):
        assert yamlutil.parse("a: 1") == yamlutil.IMPORT_ERROR_MSG


def test_parse_struct_time():
    YAML = MagicMock()
    yaml_instance = MagicMock()
    YAML.return_value = yaml_instance

    yaml_instance.load.return_value = {"t": "dummy"}

    with patch("yamlutil._load_yaml", return_value=(YAML, None)):
        result = yamlutil.parse("t: !struct_time 2024-01-01 12:00:00")
        yaml_instance.constructor.add_constructor.assert_called()
        assert yaml_instance.load.called


# ---------------------------------------------------------
# __cleanup()
# ---------------------------------------------------------

def test_cleanup_removes_empty_values():
    assert yamlutil._yamlutil__cleanup({
        "a": "",
        "b": None,
        "c": [],
        "d": {},
        "e": 0,
        "f": False,
        "g": "ok"
    }) == {"e": 0, "f": False, "g": "ok"}


def test_cleanup_nested():
    data = {
        "a": {
            "x": "",
            "y": 1
        },
        "b": [
            "",
            2,
            None,
            []
        ]
    }

    cleaned = yamlutil._yamlutil__cleanup(data)
    assert cleaned == {
        "a": {"y": 1},
        "b": [2]
    }
