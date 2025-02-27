# let's validate configurations and expect them to work or not
import os
import traceback

from click.testing import Result
from reposync import cli
from typer.testing import CliRunner

runner = CliRunner()


def _format_cli_error(result: Result) -> str:
    assert result.exception
    tb_message = "\n".join(traceback.format_tb(result.exception.__traceback__))
    return f"Below exception was raised by the cli:\n{tb_message}\n{result.stdout}"


def test_app():
    result = runner.invoke(cli.app, ["missing.yaml"])
    assert result.exit_code == os.EX_OK, _format_cli_error(result)
    assert "Hello Camila" in result.stdout
    assert "Let's have a coffee in Berlin" in result.stdout
