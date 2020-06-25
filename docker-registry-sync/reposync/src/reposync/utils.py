import traceback
import base64
import json
import yaml
import random
import string
import os

from typing import IO, Any, Dict
from contextlib import contextmanager
from pathlib import Path
from sanitize_filename import sanitize

_cached_worker_ids = set()
_cached_stage_ids = set()


class CyclicDependencyException(Exception):
    pass


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


def random_alphanumerical_string(length):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def make_task_id(length=5) -> str:
    generated_worker_id = random_alphanumerical_string(length=length)
    if generated_worker_id in _cached_worker_ids:
        return make_task_id(length=length)

    _cached_worker_ids.add(generated_worker_id)
    return generated_worker_id


def make_stage_id(proposed_id: str) -> str:
    if proposed_id is None:
        proposed_id = random_alphanumerical_string(10)
    if proposed_id in _cached_stage_ids:
        return make_stage_id(None)

    _cached_stage_ids.add(proposed_id)
    return proposed_id


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
