import os
from typing import Annotated, TypeAlias, Self

from pydantic import (
    BaseModel,
    Field,
    BeforeValidator,
    ConfigDict,
    SecretStr,
    model_validator,
)

RegistryKey: TypeAlias = str
IDKey: TypeAlias = str


def _resolve_from_env(env_var_name: str | None) -> str:
    if env_var_name is None:
        return env_var_name
    return os.environ[env_var_name]


class Registry(BaseModel):
    url: str
    env_user: Annotated[str | None, BeforeValidator(_resolve_from_env)]
    env_password: Annotated[SecretStr | None, BeforeValidator(_resolve_from_env)]
    skip_tls_verify: bool = False


class FromEntry(BaseModel):
    source: RegistryKey
    repository: str


class ToEntry(BaseModel):
    destination: RegistryKey
    repository: str
    tags: list[str]


class Stage(BaseModel):
    from_entry: Annotated[FromEntry, Field(alias="from")]
    to_entries: Annotated[list[ToEntry], Field(alias="to")]
    id: IDKey | None = None
    depends_on: Annotated[list[IDKey], Field(default_factory=list)]

    model_config = ConfigDict(populate_by_name=True)


class ConfigFile(BaseModel):
    registries: dict[RegistryKey, Registry]
    stages: list[Stage]

    @model_validator(mode="after")
    @classmethod
    def ensure_constraints(cls, model: Self) -> Self:
        all_stage_ids: list[IDKey] = [s.id for s in model.stages if s.id is not None]
        stage_ids: set[IDKey] = set(all_stage_ids)

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
