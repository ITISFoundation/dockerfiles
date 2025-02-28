# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import sys
import logging
from pathlib import Path
from typing import Callable

import pytest

_CURRENT_DIR = (
    Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().parent
)


def _set_env_from_dict(monkeypatch: pytest.MonkeyPatch, data: dict[str, str]) -> None:
    for key, value in data.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def environment(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env_from_dict(
        monkeypatch,
        {
            "ENV_VAR_FIRST_USER": "first_user",
            "ENV_VAR_FIRST_PASSWORD": "first_pwd",
            "ENV_VAR_SECOND_USER": "second_user",
            "ENV_VAR_SECOND_PASSWORD": "second_pwd",
        },
    )


@pytest.fixture
def data_path(environment: None) -> Path:
    data_dir = _CURRENT_DIR / "data"
    assert data_dir.exists()
    return data_dir


@pytest.fixture
def get_config_file(data_path: Path) -> Callable[[str], str]:
    def _(file_name: str) -> str:
        config_file = data_path / file_name
        assert config_file.exists()
        return f"{config_file}"

    return _


@pytest.fixture
def caplog_debug(caplog: pytest.LogCaptureFixture) -> pytest.LogCaptureFixture:
    caplog.clear()
    caplog.set_level(logging.DEBUG)
    return caplog
