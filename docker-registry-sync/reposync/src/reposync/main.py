import sys
import yaml
import argparse
import datetime
import subprocess
from collections import deque
from io import TextIOWrapper

from reposync.validation import is_configuration_valid
from reposync.prepare_stages import assemble_stages
from reposync.dregsy_config import create_dregsy_yamls
from reposync.utils import temp_configuration_file, from_env_default


def load_yaml_from_file(input_file: TextIOWrapper) -> str:
    with input_file as f:
        return yaml.safe_load(f)


def error_exit(start_date):
    print("\nThere were errors during sync, check the logs above")
    print(f"Error after after: {datetime.datetime.utcnow() - start_date}\n")
    exit(1)


def sync_based_on_configuration(
    configuration: str, flag_exit_on_first_error: bool, debug: bool
) -> None:
    # get stages from own configuration file
    stages = assemble_stages(configuration)
    # convert stagest to dregsy yaml format
    dregsy_entries = create_dregsy_yamls(stages)

    # will cause the process to quit if an error is detected during dregsy output
    exit_on_first_error = (
        from_env_default("SYNC_EXIT_ON_FIRST_ERROR", False) or flag_exit_on_first_error
    )

    completed_successful = True

    start_date = datetime.datetime.utcnow()

    for dregsy_entry in dregsy_entries:
        yaml_string = dregsy_entry.as_yaml()
        with temp_configuration_file(dregsy_entry.stage_file_name) as f:
            f.write(yaml_string)
            f.close()  # close to commit write changes

            header = f"| {dregsy_entry.ci_print_header} |"
            print(f"\n{'-' * len(header)}")
            print(header)
            print(f"{'-' * len(header)}")
            if debug:
                print(dregsy_entry.ci_print())

            # do our work with the file like running the command and at the end it will be automatically removed

            dregsy_command = f"dregsy -config={f.name}".split(" ")
            process = subprocess.Popen(
                dregsy_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            # stream progress in real time and monitor for errors
            current_logs = deque()
            for line in iter(process.stdout.readline, b""):
                decoded_line = line.decode()
                if (
                    "[ERROR] one or more tasks had errors, please see log for details"
                    in decoded_line
                ):
                    completed_successful = False
                    if exit_on_first_error:
                        if not debug:
                            print("".join(current_logs))
                        error_exit(start_date)
                if debug:
                    sys.stdout.write(decoded_line)
                else:
                    current_logs.append(decoded_line)

    if not completed_successful:
        error_exit(start_date)

    print(f"Image sync took: {datetime.datetime.utcnow() - start_date}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Syncs registry images based on configuration"
    )
    parser.add_argument(
        "-c",
        "--configfile",
        type=argparse.FileType("r"),
        default="sync-cfg.yaml",
        help="configuration file to be used",
    )
    parser.add_argument(
        "--verify-only",
        default=False,
        action="store_true",
        help="check configuration file only",
    )
    parser.add_argument(
        "--exit-on-first-error",
        default=False,
        action="store_true",
        help="if an error occurs do not continue sync",
    )
    parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="show additional information during sync",
    )
    # add exit on first error to force a quit
    args = parser.parse_args()

    # Configuration checking:
    # - load from yaml file
    # - validate with json schema (yml must always be mappable to json)
    # - only raise error if invalid otherwise free to use
    configuration = load_yaml_from_file(args.configfile)
    is_configuration_valid(configuration)

    if args.verify_only:
        print("Configuration is OK, closing gracefully.")
        exit(0)

    # all checks look ok, starting repository sync
    sync_based_on_configuration(configuration, args.exit_on_first_error, args.debug)


if __name__ == "__main__":
    main()

