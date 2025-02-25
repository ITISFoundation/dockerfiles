import pytest
import jsonschema

from reposync import main, utils
from argparse import Namespace


def test_cli_missing_file():
    with pytest.raises(AttributeError) as excinfo:
        main.run_app(Namespace())
    assert "object has no attribute 'configfile'" in str(excinfo.value)


def test_wrong_configuration_json_schema_not_respected(args_wrong_conf_file):
    with pytest.raises(jsonschema.exceptions.ValidationError):
        main.run_app(args_wrong_conf_file)


def test_verify_only(args_verify_only):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main.run_app(args_verify_only)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0


def test_main_starting(mocker, mocked_config):
    mocker.patch("reposync.main.queued_scheduler", return_value=None)
    result = main.run_app(mocked_config)
    assert result is None


def test_missing_env_vars_for_config(mocker, mocked_no_env_config):
    mocker.patch("reposync.main.queued_scheduler", return_value=None)
    with pytest.raises(KeyError) as excinfo:
        main.run_app(mocked_no_env_config)
    assert (
        "The following environment variables are required: ['ENV_VAR_FIRST_USER', 'ENV_VAR_FIRST_PASSWORD', 'ENV_VAR_SECOND_USER', 'ENV_VAR_SECOND_PASSWORD']"
        in str(excinfo.value)
    )


def test_multiple_ids_in_stages_for_config(mocker, mocked_no_such_stage_config):
    mocker.patch("reposync.main.queued_scheduler", return_value=None)
    with pytest.raises(KeyError) as excinfo:
        main.run_app(mocked_no_such_stage_config)
    assert "depends_on=['test-stage'] no stage with that name defined" in str(
        excinfo.value
    )


def test_stage_self_dependency_for_config(mocker, mocked_stage_self_dependency_config):
    mocker.patch("reposync.main.queued_scheduler", return_value=None)
    with pytest.raises(ValueError) as excinfo:
        main.run_app(mocked_stage_self_dependency_config)
    assert (
        "Stage test-stage cannot depend upon itself: depends_on=['test-stage']"
        in str(excinfo.value)
    )


def test_multi_stage_ids_for_config(mocker, mocked_multi_stage_ids_config):
    mocker.patch("reposync.main.queued_scheduler", return_value=None)
    with pytest.raises(KeyError) as excinfo:
        main.run_app(mocked_multi_stage_ids_config)
    assert (
        "Stage id 'test-stage' defined multiple times, check the configuration"
        in str(excinfo.value)
    )


def test_cyclic_dependency_for_config(patch_popen, cyclic_dependency_config):
    with pytest.raises(utils.CyclicDependencyException) as excinfo:
        main.run_app(cyclic_dependency_config)
    assert (
        "Please remove cyclic dependencies. Check predecessors:\n{'one.1': ['two.1'], 'two.1': ['one.1']}"
        in str(excinfo.value)
    )


def test_startup(patch_popen, mocked_config, capfd):
    main.run_app(mocked_config)

    out, _ = capfd.readouterr()
    assert "Image sync took" in out
