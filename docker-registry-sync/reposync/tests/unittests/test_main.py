import pytest
import jsonschema

from reposync import main
from argparse import Namespace


def test_cli_missing_file():
    with pytest.raises(AttributeError) as excinfo:
        main.main(Namespace())
    assert "object has no attribute 'configfile'" in str(excinfo.value)


def test_wrong_configuration_json_schema_not_respected(args_wrong_conf_file):
    with pytest.raises(jsonschema.exceptions.ValidationError):
        main.main(args_wrong_conf_file)


def test_verify_only(args_verify_only):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main.main(args_verify_only)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0


def test_main_starting(mocker, mocked_config):
    mocker.patch("reposync.main.queued_scheduler", return_value=None)
    result = main.main(mocked_config)
    assert result is None

