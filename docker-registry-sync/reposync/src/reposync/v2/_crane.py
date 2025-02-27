import asyncio
from aiocache import cached

from pydantic import SecretStr

from .models import DockerImage, DockerImageAndTag


class CraneCommandError(RuntimeError):
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
        raise CraneCommandError(command, result)

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


@cached()
async def get_digest(
    image: DockerImageAndTag, *, skip_tls_verify: bool, debug: bool
) -> str | None:
    """computes the digest of an image, results are cahced for efficnecy"""
    command = ["crane", "digest", image]
    if skip_tls_verify:
        command.append("--insecure")

    try:
        return await _execute_command(command, debug=debug)
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
    debug: bool,
) -> None:
    command = ["crane", "copy", source, destination]
    if src_skip_tls_verify or dst_skip_tls_verify:
        command.append("--insecure")
    await _execute_command(command, debug=debug)


async def get_image_tags(image: DockerImage, *, debug: bool) -> list[str]:
    response = await _execute_command(
        ["crane", "ls", image, "--omit-digest-tags"], debug=debug
    )
    return [x.strip() for x in response.strip().split("\n")]
