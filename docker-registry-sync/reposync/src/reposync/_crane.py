import asyncio
import logging
from aiocache import cached, Cache

from pydantic import SecretStr

from ._models import DockerImage, DockerImageAndTag

_logger = logging.getLogger(__name__)


class CraneCommandError(RuntimeError):
    def __init__(self, command: list[str | SecretStr], result: str):
        super().__init__(f"Command {command=} finished with error:\n{result}")


def _resolve_secret(value: str | SecretStr) -> str:
    return value.get_secret_value() if isinstance(value, SecretStr) else value


async def _execute_command(command: list[str | SecretStr]) -> str:
    process = await asyncio.create_subprocess_exec(
        *[_resolve_secret(c) for c in command],
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    stdout, _ = await process.communicate()
    result = stdout.decode()

    if process.returncode != 0:
        raise CraneCommandError(command, result)

    _logger.debug("'%s' finishe with:\n%s", command, result)

    return result


async def login(registry_url: str, username: str, password: SecretStr) -> None:
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
        ]
    )


@cached()
async def get_digest(image: DockerImageAndTag, *, skip_tls_verify: bool) -> str | None:
    """computes the digest of an image, results are cahced for efficnecy"""
    command = ["crane", "digest", image]
    if skip_tls_verify:
        command.append("--insecure")

    try:
        return await _execute_command(command)
    except CraneCommandError as e:
        if "unexpected status code 404" in f"{e}":
            return None
        raise


async def copy(
    source: DockerImageAndTag,
    destination: DockerImageAndTag,
    *,
    src_skip_tls_verify: bool,
    dst_skip_tls_verify: bool,
) -> None:
    command = ["crane", "copy", source, destination]
    if src_skip_tls_verify or dst_skip_tls_verify:
        command.append("--insecure")
    await _execute_command(command)


@cached()
async def get_image_tags(image: DockerImage) -> list[str]:
    response = await _execute_command(["crane", "ls", image, "--omit-digest-tags"])
    return [x.strip() for x in response.strip().split("\n")]


async def clear_cache() -> None:
    cache = Cache()
    await cache.clear()
