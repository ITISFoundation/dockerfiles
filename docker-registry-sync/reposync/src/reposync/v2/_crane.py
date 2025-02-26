import asyncio
from functools import lru_cache
from typing import Final

from pydantic import NonNegativeInt, SecretStr

from .models import DockerImage, DockerImageAndTag, DockerTag

_DIGEST_CACHE_SIZE: Final[NonNegativeInt] = 10_000


class CouldNotCopyError(RuntimeError):
    def __init__(self, command: list[str | SecretStr], result: str):
        super().__init__(f"Command {command=} finished with error:\n{result}")


def _resolve_secret(value: str | SecretStr) -> str:
    return value.get_secret_value() if isinstance(value, SecretStr) else value


async def _execute_command(command: list[str | SecretStr], *, debug: bool) -> str:
    process = await asyncio.create_subprocess_exec(
        *[_resolve_secret(c) for c in command],
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    stdout, _ = await process.communicate()
    result = stdout.decode()

    if process.returncode != 0:
        raise CouldNotCopyError(command, result)

    if debug:
        print(f"{command=} finishe with:\n{result}")

    return result


async def login(
    registry_url: str, username: str, password: SecretStr, *, debug: bool
) -> None:
    await _execute_command(
        [
            "crane",
            "auth",
            "login",
            registry_url,
            "--username",
            username,
            "--password",
            password,
        ],
        debug=debug,
    )


@lru_cache(maxsize=_DIGEST_CACHE_SIZE)
async def get_digest(image: DockerImage, tag: DockerTag, *, debug: bool) -> str:
    """computes the digest of an image, results are cahced for efficnecy"""
    return await _execute_command(["crane", "digest", f"{image}:{tag}"], debug=debug)


async def copy(
    source: DockerImageAndTag, destination: DockerImageAndTag, *, debug: bool
) -> None:
    await _execute_command(["crane", "copy", source, destination], debug=debug)


async def get_image_tags(image: DockerImage, *, debug: bool) -> list[str]:
    response = await _execute_command(
        ["crane", "ls", image, "--omit-digest-tags"], debug=debug
    )
    return [x.strip() for x in response.strip().split("\n")]
