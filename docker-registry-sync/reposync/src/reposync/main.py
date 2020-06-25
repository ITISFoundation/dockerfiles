import sys
import yaml
import argparse
import datetime
import traceback
import subprocess
from collections import deque
from io import TextIOWrapper
from concurrent import futures
from typing import Dict
from queue import Queue
from pprint import pprint


from reposync.validation import is_configuration_valid
from reposync.prepare_stages import assemble_stages
from reposync.dregsy_config import create_dregsy_task_graph, DregsyYAML, Task
from reposync.utils import temp_configuration_file, from_env_default, make_task_id


def load_yaml_from_file(input_file: TextIOWrapper) -> Dict:
    with input_file as f:
        return yaml.safe_load(f)


def error_exit(start_date: datetime.datetime) -> None:
    print("\nThere were errors during sync, check the logs above")
    print(f"Error after after: {datetime.datetime.utcnow() - start_date}\n")
    exit(1)


def sch_print(message: str) -> None:
    print(f"[scheduler] {message}")


def run_dregsy_task(dregsy_task: Task, results_queue: Queue, debug: bool) -> None:
    try:
        dregsy_entry = DregsyYAML.assemble([dregsy_task])
        with temp_configuration_file(dregsy_entry.stage_file_name) as f:
            f.write(dregsy_entry.as_yaml())
            f.close()  # close to commit write changes
            task_id = make_task_id()

            if debug:
                header = f"| {dregsy_entry.ci_print_header} |"
                dashes = len(header) - 2
                print(
                    f"\n{task_id}| {'-' * dashes}\n{task_id}{header}\n{task_id}| {'-' * dashes}"
                )
                print(
                    f"\n{task_id}| Below dregsy configuration\n{dregsy_entry.ci_print()}"
                )
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
        results_queue.put((completed_successfully, current_logs, dregsy_task.id))
    except Exception:
        results_queue.put((False, traceback.format_exc(), dregsy_task.id))


def queued_scheduler(configuration: str, parallel_sync_tasks: int, debug: bool) -> None:
    # get stages from own configuration file
    stages = assemble_stages(configuration)
    # compute dependency graph for execution and return predecessors
    task_mapping, predecessors = create_dregsy_task_graph(stages)

    completed_tasks = {k: False for k in task_mapping.keys()}
    already_started_tasks = set()

    results_queue = Queue()

    def predecessors_complete(task_predecessors):
        return all([completed_tasks[x] for x in task_predecessors])

    start_date = datetime.datetime.utcnow()
    overall_completed_successfully = True

    with futures.ThreadPoolExecutor(max_workers=parallel_sync_tasks) as executor:

        def schedule_wating_tasks():
            for task_id, task in task_mapping.items():
                if completed_tasks[task_id]:
                    continue  # skiping task already completed
                if not predecessors_complete(predecessors[task_id]):
                    continue  # still waiting for predecessors to finish
                if task_id in already_started_tasks:
                    continue  # task is already running

                executor.submit(run_dregsy_task, task, results_queue, debug)
                sch_print(f"started => Stage {task_id}")
                already_started_tasks.add(task_id)

        schedule_wating_tasks()  # initial scheduling

        while not all(completed_tasks.values()):
            completed_successfully, task_logs, task_id = results_queue.get()

            # mark task as completed, user has to check logs if something went wrong
            completed_tasks[task_id] = True

            if debug:
                pprint(completed_tasks)

            if not completed_successfully:
                overall_completed_successfully = False
                sch_print(f"Logs from Stage {task_id}\n" + "".join(task_logs))

            completed_task_count = len(
                [x for x in completed_tasks if completed_tasks[x]]
            )
            sch_print(
                f"completed@{completed_task_count}/{len(completed_tasks)} => Stage {task_id}"
            )
            schedule_wating_tasks()

    if not overall_completed_successfully:
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
    queued_scheduler(configuration, args.parallel_sync_tasks, args.debug)


if __name__ == "__main__":
    main()

