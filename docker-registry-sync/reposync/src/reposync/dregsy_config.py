import yaml

from typing import Dict, Tuple
from dataclasses import dataclass, field
from collections import deque

from .prepare_stages import Stage, List
from .utils import encode_credentials


class BaseSerializable:
    def to_dict(self) -> Dict:
        raise NotImplementedError("Must implement in subclass")


@dataclass
class Mapping(BaseSerializable):
    from_field: str
    to_field: str
    tags: List[str]

    def to_dict(self) -> Dict:
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

    def to_dict(self) -> Dict:
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

    def to_dict(self) -> Dict:
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

    def to_dict(self) -> Dict:
        return {"relay": self.relay, "skopeo": self.skopeo, "tasks": self.tasks}

    @classmethod
    def assemble(cls, tasks):
        return DregsyYAML(
            relay="skopeo",
            skopeo={"binady": "skopeo", "certs-dir": "/etc/skopeo/certs.d"},
            tasks=tasks,
        )


def create_dregsy_yamls(stages: List[Stage]) -> List[Tuple[str, str]]:
    result = deque()
    for k, stage in enumerate(stages):
        source_auth = encode_credentials(
            stage.from_obj.source.user, stage.from_obj.source.password
        )

        for j, to_obj in enumerate(stage.to_entries):
            target_auth = encode_credentials(
                to_obj.destination.user, to_obj.destination.password
            )
            task = Task(
                name=f"Stage {k+1}: [{j+1}/{len(stage.to_entries)}] {stage.from_obj.source.key} -> {to_obj.destination.key}",
                verbose=True,
                source=TaskRegistry(
                    registry=stage.from_obj.source.url,
                    auth=source_auth,
                    skip_tls_verify=stage.from_obj.source.skip_tls_verify,
                ).to_dict(),
                target=TaskRegistry(
                    registry=to_obj.destination.url,
                    auth=target_auth,
                    skip_tls_verify=to_obj.destination.skip_tls_verify,
                ).to_dict(),
                mappings=[
                    Mapping(
                        from_field=stage.from_obj.repository,
                        to_field=to_obj.repository,
                        tags=to_obj.tags,
                    ).to_dict()
                ],
            ).to_dict()

            dregsy_entry = DregsyYAML.assemble(tasks=[task]).to_dict()
            result.append(dregsy_entry)

    return [
        (
            x["tasks"][0]["name"],
            yaml.dump(x, allow_unicode=True, default_flow_style=False, sort_keys=False),
        )
        for x in result
    ]

