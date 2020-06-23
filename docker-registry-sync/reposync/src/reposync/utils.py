import traceback
import base64
import json
import yaml
import os

from typing import IO, Any, Dict
from contextlib import contextmanager
from pathlib import Path
from sanitize_filename import sanitize


def encode_string(message: str, encoding: str = "utf-8") -> bytes:
    return base64.b64encode(message.encode(encoding)).decode(encoding)


def encode_credentials(username: str, password: str) -> bytes:
    return encode_string(json.dumps({"username": username, "password": password}))


def from_env(env_var_name: str) -> str:
    if env_var_name not in os.environ:
        raise KeyError(f"Expected '{env_var_name}' in environment variables")
    return os.environ[env_var_name]


def from_env_default(env_var_name: str, default=None) -> str:
    return os.environ.get(env_var_name, default)


def dict_to_yaml(payload: Dict) -> str:
    return yaml.dump(
        payload, allow_unicode=True, default_flow_style=False, sort_keys=False
    )


@contextmanager
def temp_configuration_file(stage_name: str) -> IO[Any]:
    target_file = Path("/tmp") / f"{sanitize(stage_name.replace(' ', ''))}.yaml"
    try:
        f = target_file.open("w")
        yield f
    except Exception:
        traceback.print_exc()
    finally:
        f.close()
        target_file.unlink()


if __name__ == "__main__":
    # decodes the first arg on cli
    import sys

    print(base64.b64decode(sys.argv[1]))
