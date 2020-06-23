import uuid

from typing import Dict, Tuple
from dataclasses import dataclass, field
from collections import deque

from .prepare_stages import Stage, List
from .utils import encode_credentials, dict_to_yaml


class BaseSerializable:
    def as_dict(self) -> Dict:
        raise NotImplementedError("Must implement in subclass")


@dataclass
class Mapping(BaseSerializable):
    from_field: str
    to_field: str
    tags: List[str]

    def as_dict(self) -> Dict:
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

    def as_dict(self) -> Dict:
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
    mappings: List[Mapping]

    def as_dict(self) -> Dict:
        return {
            "name": self.name,
            "verbose": self.verbose,
            "source": self.source,
            "target": self.target,
            "mappings": self.mappings,
        }


@dataclass
class DregsyYAML(BaseSerializable):
    relay: str
    skopeo: Dict[str, str]
    tasks: List[Task]

    def as_dict(self) -> Dict:
        return {"relay": self.relay, "skopeo": self.skopeo, "tasks": self.tasks}

    def as_yaml(self) -> str:
        return dict_to_yaml(self.as_dict())

    def ci_print(self) -> str:
        """Returns a string usable in the CI, obscures secrets """
        dict_formatted = self.as_dict()
        # obscuring secrets in UI
        for task in dict_formatted["tasks"]:
            task["source"]["auth"] = "***"
            task["target"]["auth"] = "***"
        return dict_to_yaml(dict_formatted)

    @property
    def ci_print_header(self) -> str:
        return self.tasks[0]["name"]

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


def create_dregsy_yamls(stages: List[Stage]) -> List[DregsyYAML]:
    result = deque()
    for k, stage in enumerate(stages):
        source_auth = encode_credentials(
            stage.from_obj.source.user, stage.from_obj.source.password
        )

        for j, to_obj in enumerate(stage.to_entries):
            target_auth = encode_credentials(
                to_obj.destination.user, to_obj.destination.password
            )
            task_name = "Stage {stage_number}: [{task_number}/{total_tasks}] {from_url}/{from_repo} -> {to_url}/{to_repo}".format(
                stage_number=k + 1,
                task_number=j + 1,
                total_tasks=len(stage.to_entries),
                from_url=stage.from_obj.source.url,
                from_repo=stage.from_obj.repository,
                to_url=to_obj.destination.url,
                to_repo=to_obj.repository,
            )
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
            ).as_dict()

            result.append(DregsyYAML.assemble(tasks=[task]))

    return result

