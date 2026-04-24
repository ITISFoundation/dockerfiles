# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import os
import traceback
from pathlib import Path
from typing import Callable

from click.testing import Result
from reposync import cli
from typer.testing import CliRunner
import pytest
from pytest_mock.plugin import MockerFixture


runner = CliRunner()


@pytest.fixture
def mock_crane(mocker: MockerFixture) -> None:
    mocker.patch("reposync._crane._execute_command", return_value="")


@pytest.fixture
def tracebacks_file(tmp_path: Path) -> Path:
    return tmp_path / "tracebacks.txt"


def _format_cli_error(result: Result) -> str:
    assert result.exception
    tb_message = "\n".join(traceback.format_tb(result.exception.__traceback__))
    return f"Below exception was raised by the cli:\n{tb_message}\n{result.stdout}"


def test_config_file_missing():
    result = runner.invoke(cli.app, ["missing_config.yaml"])
    assert result.exit_code != os.EX_OK, _format_cli_error(result)
    assert "Invalid value for 'CONFIG_FILE'" in result.output


def test_tracebacks_file_required(
    mock_crane: None, get_config_file: Callable[[str], str]
):
    result = runner.invoke(cli.app, [get_config_file("min_valid_conf.yaml")])
    assert result.exit_code != os.EX_OK
    assert "--tracebacks-file" in result.output


def test_cyclic_dependency_conf(
    mock_crane: None,
    get_config_file: Callable[[str], str],
    tracebacks_file: Path,
):
    result = runner.invoke(
        cli.app,
        [
            get_config_file("cyclic_dependency_conf.yaml"),
            "--tracebacks-file",
            f"{tracebacks_file}",
            "--debug",
        ],
    )
    assert result.exit_code != os.EX_OK, _format_cli_error(result)
    assert "Please remove cyclic dependencies." in f"{result}"


def test_include(
    mock_crane: None,
    get_config_file: Callable[[str], str],
    caplog_debug: pytest.LogCaptureFixture,
    tracebacks_file: Path,
):
    result = runner.invoke(
        cli.app,
        [
            get_config_file("include_main.yaml"),
            "--tracebacks-file",
            f"{tracebacks_file}",
            "--debug",
        ],
    )
    assert result.exit_code == os.EX_OK, _format_cli_error(result)
    assert "Image sync took" in caplog_debug.text
    # Tracebacks file is always created (empty on a clean run).
    assert tracebacks_file.exists()
    assert tracebacks_file.read_text() == ""


def test_min_valid_conf(
    mock_crane: None,
    get_config_file: Callable[[str], str],
    caplog_debug: pytest.LogCaptureFixture,
    tracebacks_file: Path,
):
    result = runner.invoke(
        cli.app,
        [
            get_config_file("min_valid_conf.yaml"),
            "--tracebacks-file",
            f"{tracebacks_file}",
            "--debug",
        ],
    )
    assert result.exit_code == os.EX_OK, _format_cli_error(result)
    assert "Image sync took" in caplog_debug.text
    assert tracebacks_file.exists()
    assert tracebacks_file.read_text() == ""


def test_multi_stage_ids_conf(
    get_config_file: Callable[[str], str], tracebacks_file: Path
):
    result = runner.invoke(
        cli.app,
        [
            get_config_file("multi_stage_ids_conf.yaml"),
            "--tracebacks-file",
            f"{tracebacks_file}",
            "--debug",
        ],
    )
    assert result.exit_code != os.EX_OK, _format_cli_error(result)
    assert "stages[#].id must be unique" in f"{result}"


def test_no_such_stage_conf(
    get_config_file: Callable[[str], str], tracebacks_file: Path
):
    result = runner.invoke(
        cli.app,
        [
            get_config_file("no_such_stage_conf.yaml"),
            "--tracebacks-file",
            f"{tracebacks_file}",
            "--debug",
        ],
    )
    assert result.exit_code != os.EX_OK, _format_cli_error(result)
    assert "stage.depends_on entry" in f"{result}"


def test_stages_self_dependency_conf(
    get_config_file: Callable[[str], str], tracebacks_file: Path
):
    result = runner.invoke(
        cli.app,
        [
            get_config_file("stages_self_dependency_conf.yaml"),
            "--tracebacks-file",
            f"{tracebacks_file}",
            "--debug",
        ],
    )
    assert result.exit_code != os.EX_OK, _format_cli_error(result)
    assert "stage cannot depend on itself" in f"{result}"
