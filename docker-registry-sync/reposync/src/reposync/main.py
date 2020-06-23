import sys
import yaml
import argparse
import datetime
import subprocess
from collections import deque
from io import TextIOWrapper
from concurrent import futures

from reposync.validation import is_configuration_valid
from reposync.prepare_stages import assemble_stages
from reposync.dregsy_config import create_dregsy_yamls, DregsyYAML
from reposync.utils import temp_configuration_file, from_env_default, make_task_id


def load_yaml_from_file(input_file: TextIOWrapper) -> str:
    with input_file as f:
        return yaml.safe_load(f)


def error_exit(start_date: datetime.datetime) -> None:
    print("\nThere were errors during sync, check the logs above")
    print(f"Error after after: {datetime.datetime.utcnow() - start_date}\n")
    exit(1)


def run_dregsy_task(dregsy_entry: DregsyYAML, debug: bool):
    yaml_string = dregsy_entry.as_yaml()
    with temp_configuration_file(dregsy_entry.stage_file_name) as f:
        f.write(yaml_string)
        f.close()  # close to commit write changes
        task_id = make_task_id()

        if debug:
            header = f"| {dregsy_entry.ci_print_header} |"
            dashes = len(header) - 2
            print(
                f"\n{task_id}| {'-' * dashes}\n{task_id}{header}\n{task_id}| {'-' * dashes}"
            )
            print(f"\n{task_id}| Below dregsy configuration\n{dregsy_entry.ci_print()}")
        else:
            print(f"{task_id}| {dregsy_entry.ci_print_header}")

        # do our work with the file like running the command and at the end it will be automatically removed
        completed_successfully = True
        dregsy_command = f"dregsy -config={f.name}".split(" ")
        process = subprocess.Popen(
            dregsy_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        # stream progress in real time and monitor for errors
        current_logs = deque()

        for line in iter(process.stdout.readline, b""):
            decoded_line = f"{task_id}| {line.decode()}"
            if (
                "[ERROR] one or more tasks had errors, please see log for details"
                in decoded_line
            ):
                completed_successfully = False
            if debug:
                sys.stdout.write(decoded_line)
            else:
                current_logs.append(decoded_line)

        return completed_successfully, current_logs


def sync_based_on_configuration(
    configuration: str, parallel_sync_tasks: int, debug: bool
) -> None:
    # get stages from own configuration file
    stages = assemble_stages(configuration)
    # convert stagest to dregsy yaml format
    dregsy_entries = create_dregsy_yamls(stages)

    finished_without_errors = False
    start_date = datetime.datetime.utcnow()

    with futures.ThreadPoolExecutor(max_workers=parallel_sync_tasks) as executor:
        started_futures = deque()
        for dregsy_task in dregsy_entries:
            future = executor.submit(run_dregsy_task, dregsy_task, debug)
            started_futures.append(future)

        result = futures.wait(
            started_futures, timeout=None, return_when=futures.ALL_COMPLETED
        )

        # check the state of the future
        for done_future in result.done:
            if not done_future.done():
                print(f"Future failed: {done_future}")
                finished_without_errors = True
                continue

            future_error = done_future.exception()
            if future_error is not None:
                print(f"Future with error: {future_error}")  # not expected
                finished_without_errors = True
                continue

            finished_successfully, output = done_future.result()
            if not finished_successfully:
                print("".join(output))

        # doing this here so it can error out after printing all the errors
        if len(result.not_done) > 0:
            raise Exception(f"Some futures did not finish {result.not_done}")

        if finished_without_errors:
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
        "--parallel-sync-tasks",
        default=100,
        type=int,
        help="amount of parallel sync tasks to be run at once",
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

    print(f"Starting configuration \n{args}")
    # all checks look ok, starting repository sync
    sync_based_on_configuration(configuration, args.parallel_sync_tasks, args.debug)


if __name__ == "__main__":
    main()

