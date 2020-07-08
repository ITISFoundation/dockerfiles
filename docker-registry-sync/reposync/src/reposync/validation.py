import os
from jsonschema import Draft7Validator, validate
from collections import deque
from typing import Dict

SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "config.schema.json",
    "title": "Configuration schema",
    "description": "Provides configuration for the application",
    "type": "object",
    "properties": {
        "registries": {
            "description": "Dictionary of unique registries, the keys will be used later on",
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL where to contact the registry",
                    },
                    "env_user": {
                        "type": "string",
                        "description": "Environment variable containing the registry's username",
                    },
                    "env_password": {
                        "type": "string",
                        "description": "Environment variable containing the registry's password",
                    },
                    "skip-tls-verify": {
                        "type": "boolean",
                        "description": "Disables certificate checks when not using https registry",
                    },
                },
                "required": ["url", "env_user", "env_password"],
            },
            "minProperties": 1,
        },
        "stages": {
            "description": "List of entries used to describe repo sync actions",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from": {
                        "type": "object",
                        "description": "Source image position",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "Key name from the registries",
                            },
                            "repository": {
                                "type": "string",
                                "description": "image path in repository",
                            },
                        },
                        "required": ["source", "repository"],
                    },
                    "to": {
                        "type": "array",
                        "description": "Image destinations",
                        "items": {
                            "type": "object",
                            "description": "list of destination data",
                            "properties": {
                                "destination": {
                                    "type": "string",
                                    "description": "Key name from the registries",
                                },
                                "repository": {
                                    "type": "string",
                                    "description": "image path in repository",
                                },
                                "tags": {
                                    "type": "array",
                                    "description": "a list of tags",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["destination", "repository", "tags"],
                        },
                    },
                    "id": {
                        "type": "string",
                        "description": "global unique task id, if missing one will be assigned",
                    },
                    "depends_on": {
                        "type": "array",
                        "description": "refers to the ids of other stages, this stage will be ran after the previous are completed",
                        "items": {"type": "string"},
                    },
                },
                "required": ["from", "to"],
            },
            "minProperties": 1,
        },
    },
    "required": ["registries", "stages"],
}


def _validate_environment_vars(configuration: Dict) -> None:
    keys_to_check = deque()
    for registry in configuration["registries"].values():
        keys_to_check.append(registry["env_user"])
        keys_to_check.append(registry["env_password"])

    missing_keys = deque()
    for key in keys_to_check:
        if key not in os.environ:
            missing_keys.append(key)

    if len(missing_keys) > 0:
        raise KeyError(
            f"The following environment variables are required: {list(missing_keys)}"
        )


def _validate_stage_id_and_depends_on(configuration: Dict) -> None:
    stage_ids = set()

    # validate stage uniqueness
    for stage in configuration["stages"]:
        stage_id = stage.get("id", None)
        if stage_id is None:
            continue

        if stage_id in stage_ids:
            raise KeyError(
                f"Stage id '{stage_id}' defined multiple times, check the configuration"
            )
        stage_ids.add(stage_id)

    # validate depends_on corectness
    for stage in configuration["stages"]:
        depends_on = stage.get("depends_on", None)
        if depends_on is None:
            continue

        stage_id = stage.get("id", None)
        if stage_id in depends_on:
            raise ValueError(
                f"Stage {stage_id} cannot depend upon itself: depends_on={depends_on}"
            )
        for entry in depends_on:
            if entry not in stage_ids:
                raise KeyError(
                    f"depends_on={depends_on} no stage with that name defined"
                )


def is_configuration_valid(configuration: Dict) -> None:
    """Raises exception if configuration is not valid"""
    validate(instance=configuration, schema=SCHEMA)
    _validate_environment_vars(configuration)
    _validate_stage_id_and_depends_on(configuration)
