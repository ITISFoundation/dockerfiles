import os
from uuid import uuid4
from typing import Annotated, TypeAlias, Self

from pydantic import (
    BaseModel,
    Field,
    BeforeValidator,
    AfterValidator,
    ConfigDict,
    SecretStr,
    model_validator,
)


DockerImage: TypeAlias = str
DockerTag: TypeAlias = str
DockerImageAndTag: TypeAlias = str
RegistryKey: TypeAlias = str
StageID: TypeAlias = str
TaskID: TypeAlias = str


def _resolve_from_env(env_var_name: str | None) -> str:
    if env_var_name is None:
        return env_var_name

    if env_var_name not in os.environ:
        msg = f"The following env var must be set: '{env_var_name}'"
        raise ValueError(msg)

    return os.environ[env_var_name]


def _replace_none_stage(stage_id: StageID | None) -> StageID:
    return f"{uuid4()}" if stage_id is None else stage_id


class Registry(BaseModel):
    url: str
    env_user: Annotated[str | None, BeforeValidator(_resolve_from_env)]
    env_password: Annotated[SecretStr | None, BeforeValidator(_resolve_from_env)]
    skip_tls_verify: Annotated[bool, Field(alias="skip-tls-verify")] = False


class FromEntry(BaseModel):
    source: RegistryKey
    repository: DockerImage


class ToEntry(BaseModel):
    destination: RegistryKey
    repository: DockerImage
    tags: list[DockerTag]


class Stage(BaseModel):
    from_entry: Annotated[FromEntry, Field(alias="from")]
    to_entries: Annotated[list[ToEntry], Field(alias="to")]
    id: Annotated[
        StageID | None,
        Field(default_factory=lambda: f"{uuid4()}"),
        AfterValidator(_replace_none_stage),
    ]
    depends_on: Annotated[list[StageID], Field(default_factory=list)]

    model_config = ConfigDict(populate_by_name=True)


class Configuration(BaseModel):
    registries: dict[RegistryKey, Registry]
    stages: list[Stage]

    @model_validator(mode="after")
    @classmethod
    def ensure_constraints(cls, model: Self) -> Self:
        all_stage_ids: list[StageID] = [s.id for s in model.stages]
        stage_ids: set[StageID] = set(all_stage_ids)

        # mo duplicate IDKey
        if duplicates := {i for i in all_stage_ids if all_stage_ids.count(i) > 1}:
            msg = f"stages[#].id must be unique, {duplicates=}"
            raise ValueError(msg)

        # depends_on entry exsits
        for stage in model.stages:
            for target_id in stage.depends_on:
                if target_id not in stage_ids:
                    msg = f"stage.depends_on entry '{target_id}' must be any of {stage_ids=}"
                    raise ValueError(msg)

        for stage in model.stages:
            for to_entry in stage.to_entries:
                # destination RegistryKey exists
                if to_entry.destination not in model.registries:
                    msg = f"{to_entry.destination=} must be any of {model.registries.keys()}"
                    raise ValueError(msg)

            # source RegistryKey exsits
            from_entry = stage.from_entry
            if from_entry.source not in model.registries:
                msg = f"{from_entry.source=} must be any of {model.registries.keys()}"
                raise ValueError(msg)

        return model
