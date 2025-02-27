import asyncio
import logging
from pathlib import Path
from pprint import pformat

import typer
import yaml
from pydantic import NonNegativeInt, TypeAdapter
from typing_extensions import Annotated

from ._models import Configuration
from ._sync import run_sync_tasks

_logger = logging.getLogger(__name__)


def _configure_logging(debug: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(levelname)s: %(message)s",
    )


async def _async_app(
    configfile: Path,
    verify_only: bool,
    parallel_sync_tasks: NonNegativeInt,
    use_explicit_tags: bool,
    debug: bool,
) -> None:
    _configure_logging(debug)

    _logger.debug("Confoguration path: '%s'", configfile)

    parased_yaml = yaml.safe_load(configfile.read_text())
    configuration = TypeAdapter(Configuration).validate_python(parased_yaml)
    _logger.info(
        "Parsed configuration:\n%s", pformat(configuration.model_dump(mode="python"))
    )

    if verify_only:
        _logger.info("Configuration is OK, closing gracefully.")
        return

    # rest of the app

    await run_sync_tasks(
        configuration,
        use_explicit_tags=use_explicit_tags,
        parallel_sync_tasks=parallel_sync_tasks,
    )


def app(
    config_file: Annotated[
        Path,
        typer.Argument(help="configuration file to be used", exists=True),
    ],
    verify_only: Annotated[
        bool, typer.Option(help="check configuration file only", allow_dash=True)
    ] = False,
    parallel_sync_tasks: Annotated[
        NonNegativeInt,
        typer.Option(
            help="amount of parallel sync tasks to be run at once", allow_dash=True
        ),
    ] = 10,
    use_explicit_tags: Annotated[
        bool,
        typer.Option(
            help="if enabled tags have to be set explictly before they are synced otherwise `tags: []` is interpreted as all tags",
            allow_dash=True,
        ),
    ] = False,
    debug: Annotated[
        bool, typer.Option(help="show additional information during sync")
    ] = False,
):
    asyncio.run(
        _async_app(
            config_file, verify_only, parallel_sync_tasks, use_explicit_tags, debug
        )
    )


def main() -> None:
    typer.run(app)


if __name__ == "__main__":
    main()
