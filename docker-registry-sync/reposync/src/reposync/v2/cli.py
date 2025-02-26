from pathlib import Path

import typer
import yaml
from pydantic import NonNegativeInt, TypeAdapter
from typing_extensions import Annotated

from .models import ConfigFile


def app(
    configfile: Annotated[
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
    debug: Annotated[
        bool, typer.Option(help="show additional information during sync")
    ] = False,
):
    _ = debug
    _ = parallel_sync_tasks

    print(f"Using '{configfile=}'")

    parased_yaml = yaml.safe_load(configfile.read_text())
    config_file = TypeAdapter(ConfigFile).validate_python(parased_yaml)
    print(config_file)

    if verify_only:
        print("Configuration is OK, closing gracefully.")
        return

    # TODO: RUN sync form here
    print("continue app")


def main() -> None:
    typer.run(app)


if __name__ == "__main__":
    main()
