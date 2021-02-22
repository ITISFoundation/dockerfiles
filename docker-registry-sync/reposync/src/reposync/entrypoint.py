from argparse import ArgumentParser
from pathlib import Path

from .yaml_loader import load_yaml_file
from .parsing import validate_configuration, validate_yaml_array_file
from .graph_assembly import assemble_sync_data, SyncData
from .runner import run_parallel_upload


def is_valid_file(parser: ArgumentParser, arg) -> Path:
    path = Path(arg)
    if not path.is_file():
        parser.error("The file %s does not exist or is a directory!" % arg)
    else:
        return path


def main() -> None:
    parser = ArgumentParser(description="repo-sync tool")
    parser.add_argument(
        "-c",
        dest="config_file",
        required=True,
        help="provide a valid configuration file",
        metavar="FILE",
        type=lambda x: is_valid_file(parser, x),
    )

    args = parser.parse_args()
    config_file = args.config_file

    configuration = validate_configuration(config_file)

    sync_data: SyncData = assemble_sync_data(configuration)
    run_parallel_upload(configuration, sync_data)
    print("All sync jobs completed")


if __name__ == "__main__":
    main()
