import io
import pytest
from argparse import Namespace

MIN_VALID_CONFIGURATION = """
registries:
  first:
    url: first.url.here
    env_user: ENV_VAR_FIRST_USER
    env_password: ENV_VAR_FIRST_PASSWORD
  second:
    url: second.url.here
    env_user: ENV_VAR_SECOND_USER
    env_password: ENV_VAR_SECOND_PASSWORD

stages:
  - from:
      source: first
      repository: "some/repo"
    to:
      - destination: second
        repository: "other/repo"
        tags: []
"""


@pytest.fixture
def min_valid_conf_file_content(monkeypatch):
    monkeypatch.setenv("ENV_VAR_FIRST_USER", "first_user")
    monkeypatch.setenv("ENV_VAR_FIRST_PASSWORD", "first_pwd")
    monkeypatch.setenv("ENV_VAR_SECOND_USER", "second_user")
    monkeypatch.setenv("ENV_VAR_SECOND_PASSWORD", "second_pwd")

    return io.StringIO(MIN_VALID_CONFIGURATION)


@pytest.fixture
def mocked_config(min_valid_conf_file_content):
    config_mock = {
        "configfile": min_valid_conf_file_content,
        "parallel_sync_tasks": 100,
        "verify_only": False,
        "debug": False,
    }
    return Namespace(**config_mock)


@pytest.fixture
def args_wrong_conf_file(mocked_config):
    mocked_config.configfile = io.StringIO("wrong configuration")
    return mocked_config


@pytest.fixture
def args_verify_only(mocked_config):
    mocked_config.verify_only = True
    return mocked_config

