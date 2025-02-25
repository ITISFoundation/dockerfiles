import uuid
import networkx as nx

from dataclasses import dataclass
from collections import deque


from .prepare_stages import Stage
from .utils import encode_credentials, dict_to_yaml, CyclicDependencyException


class BaseSerializable:
    def as_dict(self) -> dict:
        raise NotImplementedError("Must implement in subclass")  # pragma: no cover


@dataclass
class Mapping(BaseSerializable):
    from_field: str
    to_field: str
    tags: list[str]
    platform: str = "all"

    def as_dict(self) -> dict:
        result = {
            "from": self.from_field,
            "to": self.to_field,
        }
        if self.tags is not None and len(self.tags) > 0:
            result["tags"] = self.tags
        return result


@dataclass
class TaskRegistry(BaseSerializable):
    registry: str
    auth: str
    skip_tls_verify: bool

    def as_dict(self) -> dict:
        return {
            "registry": self.registry,
            "auth": self.auth,
            "skip-tls-verify": self.skip_tls_verify,
        }


@dataclass
class Task(BaseSerializable):
    name: str
    verbose: bool
    source: TaskRegistry
    target: TaskRegistry
    mappings: list[Mapping]
    # needed for scheduling
    id: str
    depends_on: list[str]


@dataclass
class DregsyYAML(BaseSerializable):
    relay: str
    skopeo: dict[str, str]
    tasks: list[Task]

    def as_dict(self) -> dict:
        return {"relay": self.relay, "skopeo": self.skopeo, "tasks": self.tasks}

    def as_yaml(self) -> str:
        return dict_to_yaml(self.as_dict())

    def ci_print(self) -> str:
        """Returns a string usable in the CI, obscures secrets"""
        dict_formatted = self.as_dict()
        # obscuring secrets in UI
        for task in dict_formatted["tasks"]:
            task.source["auth"] = "***"
            task.target["auth"] = "***"
        return dict_to_yaml(dict_formatted)

    @property
    def ci_print_header(self) -> str:
        return self.tasks[0].name

    @property
    def stage_file_name(self) -> str:
        return f"{uuid.uuid4()}.yaml"

    @classmethod
    def assemble(cls, tasks):
        return DregsyYAML(
            relay="skopeo",
            skopeo={"binady": "skopeo", "certs-dir": "/etc/skopeo/certs.d"},
            tasks=tasks,
        )


def create_dregsy_task_graph(
    stages: list[Stage],
) -> tuple[dict[str, Task], dict[str, list[str]]]:
    def get_task_number(task_index):
        return task_index + 1

    def get_task_name(stage_id, task_number):
        return f"{stage_id}.{task_number}"

    # compute dependency mapping from stages to Dregsy_tasks
    dependency_remapper = {None: []}
    for stage in stages:
        dependency_remapper[stage.id] = set()
        for j, to_obj in enumerate(stage.to_entries):
            dependency_remapper[stage.id].add(
                get_task_name(stage.id, get_task_number(j))
            )

    tasks = deque()

    for stage in stages:
        source_auth = encode_credentials(
            stage.from_obj.source.user, stage.from_obj.source.password
        )

        for j, to_obj in enumerate(stage.to_entries):
            target_auth = encode_credentials(
                to_obj.destination.user, to_obj.destination.password
            )
            requires_option = (
                "" if stage.depends_on is None else f"(requires {stage.depends_on})"
            )
            task_name = "Stage {stage_id}.{task_number} {requires}: [{task_number}/{total_tasks}] {from_url}/{from_repo} -> {to_url}/{to_repo}".format(
                stage_id=stage.id,
                requires=requires_option,
                task_number=get_task_number(j),
                total_tasks=len(stage.to_entries),
                from_url=stage.from_obj.source.url,
                from_repo=stage.from_obj.repository,
                to_url=to_obj.destination.url,
                to_repo=to_obj.repository,
            )

            depends_on = set()
            for stage_depends_on in stage.depends_on:
                depends_on.update(dependency_remapper[stage_depends_on])

            task = Task(
                name=task_name,
                verbose=True,
                source=TaskRegistry(
                    registry=stage.from_obj.source.url,
                    auth=source_auth,
                    skip_tls_verify=stage.from_obj.source.skip_tls_verify,
                ).as_dict(),
                target=TaskRegistry(
                    registry=to_obj.destination.url,
                    auth=target_auth,
                    skip_tls_verify=to_obj.destination.skip_tls_verify,
                ).as_dict(),
                mappings=[
                    Mapping(
                        from_field=stage.from_obj.repository,
                        to_field=to_obj.repository,
                        tags=to_obj.tags,
                    ).as_dict()
                ],
                id=get_task_name(stage.id, get_task_number(j)),
                depends_on=depends_on,
            )
            tasks.append(task)

    task_mapping = {task.id: task for task in tasks}

    graph = nx.DiGraph()
    graph.add_nodes_from(task_mapping.keys())
    # print("NODES:", task_map.keys())
    for task in tasks:
        node_edges = [(x, task.id) for x in task.depends_on]
        graph.add_edges_from(node_edges)
        # print(node_edges, ",")

    predecessors = {}
    for node in task_mapping.keys():
        predecessors[node] = [x for x in graph.predecessors(node)]

    if not nx.is_directed_acyclic_graph(graph):
        raise CyclicDependencyException(
            f"Please remove cyclic dependencies. Check predecessors:\n{predecessors}"
        )

    return task_mapping, predecessors
