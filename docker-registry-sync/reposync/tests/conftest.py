import io
import sys
import pytest
from argparse import Namespace

import reposync

from .conf import (
    MIN_VALID_CONFIGURATION,
    MULTI_STAGE_IDS_CONFIGURATION,
    NO_SUCH_STAGE_CONFIGURATION,
    STAGES_SELF_DEPENDENCY_CONFIGURATION,
    CYCLIC_DEPENDENCY_CONFIGURATION,
)


@pytest.fixture(autouse=True)
def run_around_tests():
    # setup code here
    # no setup
    yield
    # teardown code here
    reposync.utils._cached_worker_ids = set()
    reposync.utils._cached_stage_ids = set()


def _setup_env(monkeypatch):
    monkeypatch.setenv("ENV_VAR_FIRST_USER", "first_user")
    monkeypatch.setenv("ENV_VAR_FIRST_PASSWORD", "first_pwd")
    monkeypatch.setenv("ENV_VAR_SECOND_USER", "second_user")
    monkeypatch.setenv("ENV_VAR_SECOND_PASSWORD", "second_pwd")


@pytest.fixture
def _min_valid_conf_file_content(monkeypatch):
    _setup_env(monkeypatch)
    return io.StringIO(MIN_VALID_CONFIGURATION)


@pytest.fixture
def _multi_stage_id_conf_file_content(monkeypatch):
    _setup_env(monkeypatch)
    return io.StringIO(MULTI_STAGE_IDS_CONFIGURATION)


@pytest.fixture
def _no_such_stage_file_content(monkeypatch):
    _setup_env(monkeypatch)
    return io.StringIO(NO_SUCH_STAGE_CONFIGURATION)


@pytest.fixture
def _stage_self_dependency_file_content(monkeypatch):
    _setup_env(monkeypatch)
    return io.StringIO(STAGES_SELF_DEPENDENCY_CONFIGURATION)


@pytest.fixture
def _stage_cyclic_dependency_file_content(monkeypatch):
    _setup_env(monkeypatch)
    return io.StringIO(CYCLIC_DEPENDENCY_CONFIGURATION)


@pytest.fixture
def _min_conf_no_env_setup_file_content(monkeypatch):
    return io.StringIO(MIN_VALID_CONFIGURATION)


@pytest.fixture(params=[True, False])
def _is_debug(request):
    return request.param


@pytest.fixture(params=[100, 1])
def _worker_count(request):
    return request.param


def _return_config(the_config, is_debug, worker_count):
    config_mock = {
        "configfile": the_config,
        "parallel_sync_tasks": worker_count,
        "verify_only": False,
        "debug": is_debug,
    }
    return Namespace(**config_mock)


@pytest.fixture
def mocked_config(_min_valid_conf_file_content, _is_debug, _worker_count):
    return _return_config(_min_valid_conf_file_content, _is_debug, _worker_count)


@pytest.fixture
def mocked_no_env_config(_min_conf_no_env_setup_file_content, _is_debug, _worker_count):
    return _return_config(_min_conf_no_env_setup_file_content, _is_debug, _worker_count)


@pytest.fixture
def mocked_no_such_stage_config(_no_such_stage_file_content, _is_debug, _worker_count):
    return _return_config(_no_such_stage_file_content, _is_debug, _worker_count)


@pytest.fixture
def mocked_stage_self_dependency_config(
    _stage_self_dependency_file_content, _is_debug, _worker_count
):
    return _return_config(_stage_self_dependency_file_content, _is_debug, _worker_count)


@pytest.fixture
def mocked_multi_stage_ids_config(
    _multi_stage_id_conf_file_content, _is_debug, _worker_count
):
    return _return_config(_multi_stage_id_conf_file_content, _is_debug, _worker_count)


@pytest.fixture
def cyclic_dependency_config(
    _stage_cyclic_dependency_file_content, _is_debug, _worker_count
):
    return _return_config(
        _stage_cyclic_dependency_file_content, _is_debug, _worker_count
    )


@pytest.fixture
def args_wrong_conf_file(mocked_config):
    mocked_config.configfile = io.StringIO("wrong configuration")
    return mocked_config


@pytest.fixture
def args_verify_only(mocked_config):
    mocked_config.verify_only = True
    return mocked_config


class SentinelIter:
    def __init__(self, list_of_values):
        self.list_of_values = list_of_values
        self.current = 0

    def get_value(self):
        item = self.list_of_values[self.current]
        self.current += 1
        if self.current == len(self.list_of_values):  # reset for next test
            self.current = 0
        return item

    def __contains__(self, key):
        return key in self.list_of_values


@pytest.fixture(
    params=[
        SentinelIter([b"Execution output log fine!", b""]),
        SentinelIter(
            [
                b"there was something wrong here",
                b"[ERROR] one or more tasks had errors, please see log for details",
                b"",
            ],
        ),
    ]
)
def _execution_return_value(request):
    return request.param


@pytest.fixture
def mock_sys_exit(mocker):
    mocker.patch("sys.exit", return_value=True)


@pytest.fixture
def patch_popen(mocker, mock_sys_exit, _execution_return_value):

    return_value = Namespace(
        **{"stdout": Namespace(**{"readline": _execution_return_value.get_value})}
    )
    for line in iter(return_value.stdout.readline, b""):
        decoded_line = f"{'task_id'}| {line.decode()}"
    mocker.patch("subprocess.Popen", return_value=return_value)

