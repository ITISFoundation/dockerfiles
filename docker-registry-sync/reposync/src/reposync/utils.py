import traceback
import base64
import json
import os

from typing import IO, Any
from contextlib import contextmanager
from pathlib import Path
from sanitize_filename import sanitize


def encode_string(message, encoding="utf-8"):
    return base64.b64encode(message.encode(encoding)).decode(encoding)


def encode_credentials(username, password):
    return encode_string(json.dumps({"username": username, "password": password}))


def from_env(env_var_name: str) -> str:
    if env_var_name not in os.environ:
        raise KeyError(f"Expected '{env_var_name}' in environment variables")
    return os.environ[env_var_name]


def from_env_default(env_var_name: str, default=None) -> str:
    return os.environ.get(env_var_name, default)


@contextmanager
def temp_configuration_file(stage_name: str, yaml_string: str) -> IO[Any]:
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
