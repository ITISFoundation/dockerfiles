from __future__ import annotations

from dataclasses import dataclass
from .utils import from_env, make_stage_id
from cached_property import cached_property
from collections import deque

from typing import List, Dict


@dataclass
class Registry:
    key: str
    url: str
    user: str
    password: str
    skip_tls_verify: bool

    @classmethod
    def parse_from_configuration(cls, key: str, config_entry: Dict) -> Registry:
        return Registry(
            key=key,
            url=config_entry["url"],
            user=from_env(config_entry["env_user"]),
            password=from_env(config_entry["env_password"]),
            skip_tls_verify=config_entry.get("skip-tls-verify", False),
        )


@dataclass
class From:
    source: Registry
    repository: str


@dataclass
class ToEntry:
    destination: Registry
    repository: str
    tags: List[str]


@dataclass
class Stage:
    from_obj: From
    to_entries: List[ToEntry]
    id: str
    depends_on: str


class StageParser:
    """
    Parses the configuration and returns a list of stages to execute
    derived from the stages key
    """

    def __init__(self, configuration: Dict):
        self.configuration: Dict = configuration

    @cached_property
    def registries(self) -> Dict[str:Registry]:
        return {
            k: Registry.parse_from_configuration(key=k, config_entry=registry_dict)
            for k, registry_dict in self.configuration["registries"].items()
        }

    @cached_property
    def stages(self) -> List[Stage]:
        stages = deque()
        for stage in self.configuration["stages"]:
            from_obj = From(
                source=self.registries[stage["from"]["source"]],
                repository=stage["from"]["repository"],
            )
            to_entries = [
                ToEntry(
                    destination=self.registries[entry["destination"]],
                    repository=entry["repository"],
                    tags=entry["tags"],
                )
                for entry in stage["to"]
            ]
            stage_obj = Stage(
                from_obj=from_obj,
                to_entries=to_entries,
                id=make_stage_id(stage.get("id", None)),
                depends_on=stage.get("depends_on", []),
            )
            stages.append(stage_obj)
        return list(stages)


def assemble_stages(configuration: Dict) -> List[Stage]:
    """Retruns a list of sync stages to be executed in order"""
    stage_parser = StageParser(configuration)
    stage_parser.stages  # called to compute everything
    return stage_parser.stages

