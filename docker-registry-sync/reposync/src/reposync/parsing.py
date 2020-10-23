import os
import sys
from typing import Dict, List, Union
from pathlib import Path

from pydantic import (
    constr,
    validator,
    BaseModel,
    Field,
    FilePath,
    ValidationError,
    Extra,
)
from .yaml_loader import load_yaml_file

DNSWithPort = constr(
    regex=r"^(([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])\.)*([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])(:[0-9]+)?$"
)


class CustomBaseModel(BaseModel):
    class Config:
        extra = Extra.forbid


class ConfigurationRegistry(CustomBaseModel):
    user: str = Field(
        ..., description="environment variable containing the registry user name"
    )
    password: str = Field(
        ..., description="environment variable containing the registry password"
    )
    disable_delete: bool = Field(
        False,
        description="disable image removal for this registry; no images will be deleted",
    )
    tls_verify: bool = Field(
        True,
        description="enforces certificate verification",
    )

    @validator("user")
    @classmethod
    def user_from_environment(cls, v):
        if v not in os.environ:
            raise ValueError("environment variable not defined")
        return os.environ[v]

    @validator("password")
    @classmethod
    def password_from_environment(cls, v):
        if v not in os.environ:
            raise ValueError("environment variable not defined")
        return os.environ[v]


class ConfigurationSyncStepTo(CustomBaseModel):
    destination: str = Field(
        ...,
        description="full path where to sync the image without its tag",
    )
    tags: Union[FilePath, List[str]] = Field(
        ...,
        description=(
            "list of tag names to by synced(tags which are not present are removed); "
            "if a string is provided it reppresents the path to a yaml array file containing all the tags to sync"
        ),
    )
    email_owners_upon_publishing: bool = Field(
        False,
        description="if True an email will be sent to the owner when a new tag is pushed",
    )


class ConfigurationSyncStep(CustomBaseModel):
    from_field: str = Field(
        ...,
        alias="from",
        description="full path from where to sync the image without its tag",
    )
    to_fields: List[ConfigurationSyncStepTo] = Field(
        alias="to",
        description="list of repositories",
    )
    name: Union[str, None] = Field(
        None,
        description="name of the current step, used to be used in other jobs to indicate they depend upon this one",
    )
    before: Union[List[str], None] = Field(
        None,
        description="list of job names to be finished before running the current one",
    )


class Configuration(CustomBaseModel):
    max_parallel_syncs: int = Field(
        sys.maxsize,
        alias="max-parallel-syncs",
        description="maximum number of parallel syncs to run at once, default is 0 meaning all of them",
    )
    published_image_catalogs: Dict[DNSWithPort, FilePath] = Field(
        ...,
        alias="published-image-catalogs",
        description="image catalogs cotain images which need to be kept (or synced if missing) at the target registry",
    )
    registries: Dict[DNSWithPort, ConfigurationRegistry] = Field(
        ...,
        description="registries and their credentials to be used for the configuration step",
    )

    sync_steps: List[ConfigurationSyncStep] = Field(
        ...,
        alias="sync-steps",
        description="list of sync operations to be launched; a sync graph will be created for massive parallelism",
    )

    def get_dns_from_image(self, image: str) -> DNSWithPort:
        """Returns the image's DNS or raises an error"""
        parts = image.split("/")
        if not parts:
            raise ValueError(f"Could not determine DNS from image '{image}'")

        dns = parts[0]
        if dns not in self.registries:
            raise ValueError(
                f"Could not find DNS '{dns}' inside configured registries '{list(self.registries.keys())}'"
            )

        return dns

    def image_requires_tls_verify(self, image: str) -> bool:
        dns = self.get_dns_from_image(image)
        return self.registries[dns].tls_verify


class SyncPayload(CustomBaseModel):
    """Used only for syncing not for validating configration"""

    from_field: str = Field(
        ...,
        description="full path from where to sync the image without its tag",
    )
    to_field: ConfigurationSyncStepTo = Field(
        description="list of repositories",
    )


class YamlArrayFile(CustomBaseModel):
    __root__: List[str] = Field(..., description="list of strings")

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]


def validate_configuration(configuration_file: Path) -> Configuration:
    data = load_yaml_file(configuration_file)
    try:
        return Configuration(**data)
    except ValidationError as e:
        print(f"Error while validating {configuration_file}")
        raise e


def validate_yaml_array_file(yaml_array_file: Path) -> List[str]:
    data = load_yaml_file(yaml_array_file)
    try:
        return YamlArrayFile(__root__=data).__root__
    except ValidationError as e:
        print(f"Error while validating {yaml_array_file}")
        raise e