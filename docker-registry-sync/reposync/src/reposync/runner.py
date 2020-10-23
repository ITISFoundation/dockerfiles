import asyncio
import traceback
import sys

from dataclasses import dataclass
from collections import deque
from typing import List, Dict, Set
from pathlib import Path

from .graph_assembly import SyncData
from .parsing import (
    Configuration,
    SyncPayload,
    DNSWithPort,
    ConfigurationRegistry,
    validate_yaml_array_file,
)
from .skopeo import skopeo_login, skopeo_sync_image
from .exceptions import ExecpionsInSyncTasksDetected


class LockedContext:
    __slots__ = (
        "_lock",
        "_started_tasks",
        "_finished_tasks",
        "_finished_tasks_count",
        "_running_tasks_count",
    )

    def __init__(self):
        self._started_tasks: Set[str] = set()
        self._finished_tasks: Set[str] = set()
        self._finished_tasks_count: int = 0
        self._lock = asyncio.Lock()
        self._running_tasks_count: int = 0

    async def started_task_add(self, task_name) -> None:
        async with self._lock:
            self._started_tasks.add(task_name)
            self._running_tasks_count += 1

    async def finished_task_add(self, task_name) -> None:
        async with self._lock:
            self._finished_tasks.add(task_name)

    async def in_started_tasks(self, task_name) -> bool:
        async with self._lock:
            return task_name in self._started_tasks

    async def in_finished_tasks(self, task_name) -> bool:
        async with self._lock:
            return task_name in self._finished_tasks

    async def get_finished_tasks(self) -> Set[str]:
        async with self._lock:
            return self._finished_tasks

    async def inc_finished_tasks_count(self) -> None:
        async with self._lock:
            self._finished_tasks_count += 1
            self._running_tasks_count -= 1

    async def get_finished_tasks_count(self) -> int:
        async with self._lock:
            return self._finished_tasks_count

    async def get_running_tasks_count(self) -> int:
        async with self._lock:
            return self._running_tasks_count


_results_queue = asyncio.Queue()
locked_context = LockedContext()


async def login_on_all_registries(configuration: Configuration) -> None:
    print("Logging in to:")
    for dns, registry_configuration in configuration.registries.items():
        dns: DNSWithPort = dns
        registry_configuration: ConfigurationRegistry = registry_configuration
        print(f"🔐 '{dns}'")
        await skopeo_login(
            dns,
            registry_configuration.user,
            registry_configuration.password,
            registry_configuration.tls_verify,
        )


async def run_task(
    configuration: Configuration, sync_name: str, sync_payload: SyncPayload
) -> None:
    async def payload_can_throw_error():
        tasks = deque()
        source_image = sync_payload.from_field

        tags = sync_payload.to_field.tags
        # transform into array of files
        if isinstance(tags, Path):
            tags = validate_yaml_array_file(tags)

        for tag in tags:
            destination_image = f"{sync_payload.to_field.destination}:{tag}"

            task = asyncio.ensure_future(
                skopeo_sync_image(
                    source_image=source_image,
                    destination_image=destination_image,
                    source_tls_verify=configuration.image_requires_tls_verify(
                        source_image
                    ),
                    destination_tls_verify=configuration.image_requires_tls_verify(
                        destination_image
                    ),
                )
            )
            tasks.append(task)

        exceptions_detected = False
        for task in tasks:
            try:
                await task
            except Exception:
                exceptions_detected = True
                print(f"❌ {sync_name}\n{traceback.format_exc()}")

        # raise all detected exceptions
        if exceptions_detected:
            raise ExecpionsInSyncTasksDetected("Please check the above logs")

    async def runner():
        try:
            await payload_can_throw_error()
            await _results_queue.put((False, sync_name, None))
        except Exception:
            await _results_queue.put((True, sync_name, traceback.format_exc()))

    await locked_context.started_task_add(sync_name)
    asyncio.get_event_loop().create_task(runner())


async def schedule_unfinished_tasks(
    configuration: Configuration,
    sync_names_to_sync_payloads: Dict[str, SyncPayload],
    predecessors: Dict[str, List[str]],
) -> None:
    max_parallel_syncs = configuration.max_parallel_syncs
    # if task was not started and task is not finished and all preceding tasks finished
    #   then schedule task

    for sync_name, preceding_tasks in predecessors.items():
        finished_tasks = await locked_context.get_finished_tasks()
        if (
            not await locked_context.in_started_tasks(sync_name)
            and not await locked_context.in_finished_tasks(sync_name)
            # all preceding tasks had finished
            and all(x in finished_tasks for x in preceding_tasks)
            # parallel jobs check
            and await locked_context.get_running_tasks_count() < max_parallel_syncs
        ):
            await run_task(
                configuration, sync_name, sync_names_to_sync_payloads[sync_name]
            )


async def start_parallel(configuration: Configuration, sync_data: SyncData) -> None:
    await login_on_all_registries(configuration)

    sync_names_to_sync_payloads, predecessors = sync_data
    sync_names_to_sync_payloads: Dict[str, SyncPayload] = sync_names_to_sync_payloads
    predecessors: Dict[str, List[str]] = predecessors

    sync_amount = (
        "all items at once"
        if configuration.max_parallel_syncs == sys.maxsize
        else f"in batches of '{configuration.max_parallel_syncs}'"
    )
    print(f"\nWill sync {sync_amount} from:")
    for sync_name, preceding_tasks in predecessors.items():
        if len(preceding_tasks) == 0:
            print(f"🏁 '{sync_name}' has no dependencies")
        else:
            print(
                f"⏱ x{len(preceding_tasks)} '{sync_name}' requires '{preceding_tasks}'"
            )

    total_tasks = len(predecessors)

    print("\nSyncTasks results:")
    sync_exceptions = deque()
    while await locked_context.get_finished_tasks_count() < total_tasks:
        # schedule all remainign tasks if possible
        await schedule_unfinished_tasks(
            configuration,
            sync_names_to_sync_payloads,
            predecessors,
        )
        # recover finished job status and results
        with_exceptions, finished_task_name, error_message = await _results_queue.get()

        if with_exceptions:
            sync_exceptions.append((finished_task_name, error_message))
            print(f"❌ {finished_task_name} had issues, look below at the logs")
        else:
            print(f"✅ {finished_task_name} finished with no issues")

        await locked_context.finished_task_add(finished_task_name)
        await locked_context.inc_finished_tasks_count()

    # print all exceptions for finished tasks at the end
    if sync_exceptions:
        print("\nTasks with exceptions below")
    for task_name, traceback_message in sync_exceptions:
        print(f"❌SyncTask '{task_name}' finished with exceptions:\n{traceback_message}")

    # TODO: fail in case of errors
    # TODO: removal procedure with skopeo


def run_parallel_upload(configuration: Configuration, sync_data: SyncData) -> None:
    asyncio.get_event_loop().run_until_complete(
        start_parallel(configuration, sync_data)
    )