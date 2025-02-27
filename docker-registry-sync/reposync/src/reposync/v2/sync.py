from .models import Configuration
from networkx import DiGraph, is_directed_acyclic_graph
from dataclasses import dataclass
from pydantic import NonNegativeInt
from typing import Any, Coroutine
import asyncio
from concurrent.futures import ThreadPoolExecutor
from . import _crane
from datetime import datetime, timezone

from .models import (
    TaskID,
    StageID,
    DockerTag,
    DockerImage,
    DockerImageAndTag,
    RegistryKey,
    Stage,
    FromEntry,
    ToEntry,
)


class CyclicDependencyError(RuntimeError):
    pass


@dataclass(frozen=True)
class SyncTask:
    task_id: TaskID
    stage_id: StageID

    src: RegistryKey
    dst: RegistryKey

    src_path: DockerImage
    dst_path: DockerImage
    tag: DockerTag


async def _login_on_all_registries(configuration: Configuration, debug: bool) -> None:
    for registry in configuration.registries.values():
        print(f"logging into {registry.url=}")
        await _crane.login(
            registry.url, registry.env_user, registry.env_password, debug=debug
        )


async def _get_all_tags(
    image: DockerImage,
    defined_tags: list[DockerTag],
    *,
    use_explicit_tags: bool,
    debug: bool,
) -> list[DockerTag]:
    if len(defined_tags) == 0 and not use_explicit_tags:
        return await _crane.get_image_tags(image, debug=debug)
    return defined_tags


def _get_task_id(
    stage_id: StageID, from_entry: FromEntry, to_entry: ToEntry, tag: DockerTag
) -> TaskID:
    """generates a unique id between all tasks"""
    return (
        f"{from_entry.source}/{from_entry.repository}:{tag}"
        " --> "
        f"{to_entry.destination}/{to_entry.repository}:{tag}"
        f" #{stage_id}"
    )


async def _get_sync_tasks(
    configuration: Configuration, *, use_explicit_tags: bool, debug: bool
) -> list[SyncTask]:

    sync_tasks: list[SyncTask] = []

    for stage in configuration.stages:
        from_entry = stage.from_entry
        for to_entry in stage.to_entries:
            tags_to_sync = await _get_all_tags(
                from_entry.repository,
                to_entry.tags,
                use_explicit_tags=use_explicit_tags,
                debug=debug,
            )

            for tag in tags_to_sync:
                task_id = _get_task_id(stage.id, from_entry, to_entry, tag)
                print(f"Will sync '{task_id}'")
                sync_task = SyncTask(
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

    print(f"Generated '{len(sync_tasks)}' sync tasks.")

    return sync_tasks


def _get_tasks_to_run(
    configuration: Configuration, sync_tasks: list[SyncTask]
) -> tuple[dict[TaskID, SyncTask], dict[TaskID, list[TaskID]]]:
    stage_mapping: dict[StageID, Stage] = {s.id: s for s in configuration.stages}
    task_mapping: dict[TaskID, SyncTask] = {task.task_id: task for task in sync_tasks}

    if len(task_mapping) != len(sync_tasks):
        msg = f"Issue deteceted size of task_mapping {len(task_mapping)} != {len(sync_tasks)} number of sync_tasks"
        raise ValueError(msg)

    stage_to_tasks_mapping: dict[StageID, set[SyncTask]] = {}

    for task in sync_tasks:
        if task.stage_id not in stage_to_tasks_mapping:
            stage_to_tasks_mapping[task.stage_id] = set()

        stage_to_tasks_mapping[task.stage_id].add(task)

    graph = DiGraph()
    graph.add_nodes_from(task_mapping.keys())
    # print("NODES:", task_mapping.keys())
    for task in sync_tasks:
        task_depedns_on: list[StageID] = stage_mapping[task.stage_id].depends_on

        tasks_required_to_finish: set[TaskID] = set()
        for stage_id in task_depedns_on:
            tasks_in_stage = stage_to_tasks_mapping[stage_id]
            for stage_task in tasks_in_stage:
                tasks_required_to_finish.add(stage_task.task_id)

        node_edges = [(task_id, task.task_id) for task_id in tasks_required_to_finish]
        graph.add_edges_from(node_edges)
        # print(node_edges, ",")

    predecessors: dict[TaskID, list[TaskID]] = {}
    for node in task_mapping.keys():
        predecessors[node] = [x for x in graph.predecessors(node)]

    if not is_directed_acyclic_graph(graph):
        raise CyclicDependencyError(
            f"Please remove cyclic dependencies. Check predecessors:\n{predecessors}"
        )
    return task_mapping, predecessors


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


def _get_image(*, url: str, image: DockerImage, tag: DockerTag) -> DockerImageAndTag:
    return f"{url}/{image}:{tag}"


async def _copy_image(
    configuration: Configuration,
    task_mapping: dict[TaskID, SyncTask],
    task_id: TaskID,
    *,
    debug: bool,
) -> None:
    print(f"Starting '{task_id}'")

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
        src_image, skip_tls_verify=src_registry.skip_tls_verify, debug=debug
    )
    dst_digest = await _crane.get_digest(
        dst_image, skip_tls_verify=dst_registry.skip_tls_verify, debug=debug
    )

    if src_digest is not None and dst_digest is not None and src_digest == dst_digest:
        print(f"Same digest detected, skipping copy for '{task_id}'")
        return

    await _crane.copy(
        src_image,
        dst_image,
        src_skip_tls_verify=src_registry.skip_tls_verify,
        dst_skip_tls_verify=dst_registry.skip_tls_verify,
        debug=debug,
    )
    print(f"Completed '{task_id}'")


async def _run_sync_tasks(
    configuration: Configuration,
    task_mapping: dict[TaskID, SyncTask],
    predecessors: dict[TaskID, list[TaskID]],
    *,
    parallel_sync_tasks: NonNegativeInt,
    debug: bool,
) -> None:
    print(f"{task_mapping=}")
    print(f"{predecessors=}")

    # put together in which order the taska need to run
    run_batches: list[set[TaskID]] = []

    for task_id, requirements in predecessors.items():
        if len(requirements) > 0:
            run_batches.append(set(requirements))

    remaning_tasks = {task_id for task_id in predecessors}
    if len(remaning_tasks) > 0:
        run_batches.append(remaning_tasks)

    # due to the dependecy graph the same task can be scheduled multiple times
    # ensure it is only ran once
    no_duplicates_run_batches = _remove_duplicates(run_batches)

    print(f"{run_batches=}")
    print(f"{no_duplicates_run_batches=}")

    sync_oprations_count = sum([len(x) for x in no_duplicates_run_batches])
    if len(task_mapping) != sync_oprations_count:
        raise RuntimeError("something went worng sizes do not match")

    # run sync batches in order
    for batch_to_run in no_duplicates_run_batches:
        sync_coros = [
            _copy_image(configuration, task_mapping, task_id, debug=debug)
            for task_id in batch_to_run
        ]
        results = await _run_coroutines(
            sync_coros, parallel_sync_tasks=parallel_sync_tasks
        )
        if any(isinstance(x, BaseException) for x in results):
            msg = f"Could not ocmplete {results}"
            raise RuntimeError(msg)


async def run_sync_tasks(
    configuration: Configuration,
    *,
    use_explicit_tags: bool,
    parallel_sync_tasks: NonNegativeInt,
    debug: bool,
) -> None:
    await _login_on_all_registries(configuration, debug=debug)

    sync_tasks: list[SyncTask] = await _get_sync_tasks(
        configuration, use_explicit_tags=use_explicit_tags, debug=debug
    )

    task_mapping, predecessors = _get_tasks_to_run(configuration, sync_tasks)

    start_datetime = datetime.now(timezone.utc)

    await _run_sync_tasks(
        configuration,
        task_mapping,
        predecessors,
        parallel_sync_tasks=parallel_sync_tasks,
        debug=debug,
    )

    print(f"Image sync took: {datetime.now(timezone.utc) - start_datetime}")
