import os
from jsonschema import Draft7Validator, validate
from collections import deque

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
                },
                "required": ["from", "to"],
            },
            "minProperties": 1,
        },
    },
    "required": ["registries", "stages"],
}


def _validate_environment_vars(configuration: str) -> None:
    keys_to_check = deque()
    for registry in configuration["registries"].values():
        keys_to_check.append(registry["env_user"])
        keys_to_check.append(registry["env_password"])

    missing_keys = deque()
    for key in keys_to_check:
        if key not in os.environ:
            missing_keys.append(key)

    raise KeyError(
        f"The following environment variables are required: {list(missing_keys)}"
    )


def is_configuration_valid(configuration: str) -> None:
    """Raises exception if configuration is not valid"""
    validate(instance=configuration, schema=SCHEMA)
    _validate_environment_vars(configuration)
