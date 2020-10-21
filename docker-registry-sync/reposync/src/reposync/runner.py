import traceback
import sys

from dataclasses import dataclass
from collections import deque
from typing import List, Dict, Set

import asyncio

from .graph_assembly import SyncData
from .parsing import Configuration, SyncPayload


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


async def run_task(sync_name: str, sync_payload: SyncPayload) -> None:
    async def payload_can_throw_error():
        await asyncio.sleep(2)

    async def runner():
        try:
            await payload_can_throw_error()
            await _results_queue.put((False, sync_name, None))
        except Exception:
            await _results_queue.put((True, sync_name, traceback.format_exc()))

    await locked_context.started_task_add(sync_name)
    asyncio.get_event_loop().create_task(runner())


async def schedule_unfinished_tasks(
    max_parallel_syncs: int,
    sync_names_to_sync_payloads: Dict[str, SyncPayload],
    predecessors: Dict[str, List[str]],
) -> None:
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
            await run_task(sync_name, sync_names_to_sync_payloads[sync_name])


async def start_parallel(configuration: Configuration, sync_data: SyncData) -> None:
    sync_names_to_sync_payloads, predecessors = sync_data
    sync_names_to_sync_payloads: Dict[str, SyncPayload] = sync_names_to_sync_payloads
    predecessors: Dict[str, List[str]] = predecessors

    sync_amount = (
        "all items at once"
        if configuration.max_parallel_syncs == sys.maxsize
        else f"in batches of '{configuration.max_parallel_syncs}'"
    )
    print(f"Will sync {sync_amount} from:")
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
            configuration.max_parallel_syncs,
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
        print("\n⚠Tasks with exceptions below")
    for task_name, traceback_message in sync_exceptions:
        print(f"SyncTask '{task_name}' finished with exceptions:\n{traceback_message}")

    # TODO: fail in case of errors
    # TODO: removal procedure with skopeo


def run_parallel_upload(configuration: Configuration, sync_data: SyncData) -> None:
    asyncio.get_event_loop().run_until_complete(
        start_parallel(configuration, sync_data)
    )
