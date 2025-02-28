import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Coroutine
from pathlib import Path

from networkx import DiGraph, is_directed_acyclic_graph
from pydantic import NonNegativeInt

from . import _crane
from ._models import (
    Configuration,
    DockerImage,
    RegistryImage,
    DockerTag,
    FromEntry,
    RegistryKey,
    Stage,
    StageID,
    TaskID,
    ToEntry,
)

_logger = logging.getLogger(__name__)


class CyclicDependencyError(RuntimeError):
    def __init__(self, predecessors: dict[TaskID, list[TaskID]]):
        super().__init__(
            f"Please remove cyclic dependencies. Check predecessors:\n{predecessors}"
        )


@dataclass(frozen=True)
class _SyncTask:
    task_id: TaskID
    stage_id: StageID

    src: RegistryKey
    dst: RegistryKey

    src_path: DockerImage
    dst_path: DockerImage
    tag: DockerTag


async def _login_into_all_registries(configuration: Configuration) -> None:
    for registry in configuration.registries.values():
        _logger.debug("logging into '%s'", registry.url)
        await _crane.login(registry.url, registry.env_user, registry.env_password)


async def _get_tags_to_sync(
    image: RegistryImage, defined_tags: list[DockerTag], *, use_explicit_tags: bool
) -> list[DockerTag]:
    # if `use_explicit_tags is False` and `tags: []` in the configuration
    # it will fetch all tags from the remote repository
    if len(defined_tags) == 0 and not use_explicit_tags:
        return await _crane.get_image_tags(image)
    return defined_tags


def _get_unique_task_id(
    stage_id: StageID, from_entry: FromEntry, to_entry: ToEntry, tag: DockerTag
) -> TaskID:
    return (
        f"{from_entry.source}/{from_entry.repository}:{tag}"
        " --> "
        f"{to_entry.destination}/{to_entry.repository}:{tag}"
        f" #{stage_id}"
    )


def _get_image(
    *, url: str, image: DockerImage, tag: DockerTag | None = None
) -> RegistryImage:
    image_path = f"{url}/{image.lstrip('/')}"
    return image_path if tag is None else f"{image_path}:{tag}"


async def _get_sync_tasks(
    configuration: Configuration, *, use_explicit_tags: bool
) -> list[_SyncTask]:

    sync_tasks: list[_SyncTask] = []

    for stage in configuration.stages:
        from_entry = stage.from_entry
        for to_entry in stage.to_entries:
            tags_to_sync = await _get_tags_to_sync(
                _get_image(
                    url=configuration.registries[from_entry.source].url,
                    image=from_entry.repository,
                ),
                to_entry.tags,
                use_explicit_tags=use_explicit_tags,
            )

            for tag in tags_to_sync:
                task_id = _get_unique_task_id(stage.id, from_entry, to_entry, tag)
                _logger.debug("Will sync '%s'", task_id)
                sync_task = _SyncTask(
                    task_id=task_id,
                    stage_id=stage.id,
                    src=from_entry.source,
                    dst=to_entry.destination,
                    src_path=from_entry.repository,
                    dst_path=to_entry.repository,
                    tag=tag,
                )
                sync_tasks.append(sync_task)

    task_ids: list[TaskID] = [t.task_id for t in sync_tasks]

    if len(task_ids) != len(sync_tasks):
        msg = (
            f"Generated '{len(sync_tasks)}' sync tasks but "
            f"only found '{len(task_ids)}' unique tasks: {sync_tasks=}"
        )
        raise RuntimeError(msg)

    _logger.info("Generated '%s' sync tasks.", len(sync_tasks))

    return sync_tasks


@dataclass
class ExecutionPlan:
    task_mapping: dict[TaskID, _SyncTask]
    predecessors: dict[TaskID, list[TaskID]]


def _get_execution_plan(
    configuration: Configuration, sync_tasks: list[_SyncTask]
) -> ExecutionPlan:
    """transforms stage dependencies into ordered groups of sync tasks to run in parallel"""

    stage_mapping: dict[StageID, Stage] = {s.id: s for s in configuration.stages}
    task_mapping: dict[TaskID, _SyncTask] = {task.task_id: task for task in sync_tasks}

    if len(task_mapping) != len(sync_tasks):
        msg = f"Issue deteceted size of task_mapping {len(task_mapping)} != {len(sync_tasks)} number of sync_tasks"
        raise ValueError(msg)

    stage_to_tasks_mapping: dict[StageID, set[_SyncTask]] = {}

    for task in sync_tasks:
        if task.stage_id not in stage_to_tasks_mapping:
            stage_to_tasks_mapping[task.stage_id] = set()

        stage_to_tasks_mapping[task.stage_id].add(task)

    graph = DiGraph()
    graph.add_nodes_from(task_mapping.keys())
    for task in sync_tasks:
        task_depedns_on: list[StageID] = stage_mapping[task.stage_id].depends_on

        tasks_required_to_finish: set[TaskID] = set()
        for stage_id in task_depedns_on:
            tasks_in_stage = stage_to_tasks_mapping[stage_id]
            for stage_task in tasks_in_stage:
                tasks_required_to_finish.add(stage_task.task_id)

        node_edges = [(task_id, task.task_id) for task_id in tasks_required_to_finish]
        graph.add_edges_from(node_edges)

    predecessors: dict[TaskID, list[TaskID]] = {}
    for node in task_mapping.keys():
        predecessors[node] = [x for x in graph.predecessors(node)]

    if not is_directed_acyclic_graph(graph):
        raise CyclicDependencyError(predecessors)
    return ExecutionPlan(task_mapping, predecessors)


async def _copy_image(
    configuration: Configuration, task_mapping: dict[TaskID, _SyncTask], task_id: TaskID
) -> None:
    _logger.info("Starting '%s'", task_id)
    start_datetime = datetime.now(timezone.utc)

    sync_task = task_mapping[task_id]
    src_registry = configuration.registries[sync_task.src]
    dst_registry = configuration.registries[sync_task.dst]

    src_image = _get_image(
        url=src_registry.url, image=sync_task.src_path, tag=sync_task.tag
    )
    dst_image = _get_image(
        url=dst_registry.url, image=sync_task.dst_path, tag=sync_task.tag
    )

    src_digest = await _crane.get_digest(
        src_image, skip_tls_verify=src_registry.skip_tls_verify
    )
    dst_digest = await _crane.get_digest(
        dst_image, skip_tls_verify=dst_registry.skip_tls_verify
    )

    if src_digest is not None and dst_digest is not None and src_digest == dst_digest:
        _logger.info(
            "Same digest detected, skipping copy for '%s' after %s",
            task_id,
            datetime.now(timezone.utc) - start_datetime,
        )
        return

    await _crane.copy(
        src_image,
        dst_image,
        src_skip_tls_verify=src_registry.skip_tls_verify,
        dst_skip_tls_verify=dst_registry.skip_tls_verify,
    )
    _logger.info(
        "Completed '%s' in %s", task_id, datetime.now(timezone.utc) - start_datetime
    )


def _remove_duplicates(run_batches: list[set[TaskID]]) -> list[set[TaskID]]:
    seen: set[TaskID] = set()
    result: list[set[TaskID]] = []

    for batch in run_batches:
        new_batch = set()
        for entry in batch:
            if entry not in seen:
                seen.add(entry)
                new_batch.add(entry)
        result.append(new_batch)

    return result


async def _run_coroutines(
    coros: Coroutine, *, parallel_sync_tasks: NonNegativeInt
) -> list[Any]:
    with ThreadPoolExecutor(max_workers=parallel_sync_tasks) as executor:
        loop = asyncio.get_running_loop()

        tasks = [loop.run_in_executor(executor, asyncio.run, coro) for coro in coros]
        result = await asyncio.gather(*tasks, return_exceptions=True)

    return result


async def _run_sync_tasks(
    configuration: Configuration,
    execution_plan: ExecutionPlan,
    *,
    parallel_sync_tasks: NonNegativeInt,
) -> None:
    """given an execution plan:
    - removes previous entries which have been ran in previous group
    - runs each group of tasks in parallel till it finishes
    """

    # put together in which order the taska need to run
    run_batches: list[set[TaskID]] = []

    for _, requirements in execution_plan.predecessors.items():
        if len(requirements) > 0:
            run_batches.append(set(requirements))

    remaning_tasks = {task_id for task_id in execution_plan.predecessors}
    if len(remaning_tasks) > 0:
        run_batches.append(remaning_tasks)

    # due to the dependecy graph the same task can be scheduled multiple times
    # ensure it is only ran once
    no_duplicates_run_batches = _remove_duplicates(run_batches)

    sync_oprations_count = sum([len(x) for x in no_duplicates_run_batches])
    if len(execution_plan.task_mapping) != sync_oprations_count:
        raise RuntimeError("something went worng sizes do not match")

    # run sync batches in order
    for batch_to_run in no_duplicates_run_batches:
        sync_coros = [
            _copy_image(configuration, execution_plan.task_mapping, task_id)
            for task_id in batch_to_run
        ]
        results = await _run_coroutines(
            sync_coros, parallel_sync_tasks=parallel_sync_tasks
        )
        if any(isinstance(x, BaseException) for x in results):
            msg = f"Could not ocmplete {results}"
            raise RuntimeError(msg)

        # NOTE: image tags and digests are cached
        # if after a batch something changes inside a source, due to th cahce
        # it is not possible to figure it out
        # safest approach is to remove the cache
        await _crane.clear_cache()


async def run_sync_tasks(
    configuration: Configuration,
    *,
    use_explicit_tags: bool,
    parallel_sync_tasks: NonNegativeInt,
) -> None:
    await _login_into_all_registries(configuration)

    sync_tasks: list[_SyncTask] = await _get_sync_tasks(
        configuration, use_explicit_tags=use_explicit_tags
    )

    execution_plan = _get_execution_plan(configuration, sync_tasks)

    start_datetime = datetime.now(timezone.utc)

    await _run_sync_tasks(
        configuration, execution_plan, parallel_sync_tasks=parallel_sync_tasks
    )

    _logger.info("Image sync took: %s", datetime.now(timezone.utc) - start_datetime)
