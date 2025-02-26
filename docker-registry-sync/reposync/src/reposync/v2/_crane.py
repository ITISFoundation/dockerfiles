import asyncio
from pydantic import SecretStr


def _resolve_secret(value: str | SecretStr) -> str:
    return value.get_secret_value() if isinstance(value, SecretStr) else value


async def _execute_command(command: list[str | SecretStr], *, debug: bool) -> str:
    process = await asyncio.create_subprocess_exec(
        *[_resolve_secret(c) for c in command],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, _ = await process.communicate()
    result = stdout.decode()

    if process.returncode == 0:
        msg = f"Command {command=} finished with error:\n{result}"
        raise RuntimeError(msg)

    if debug:
        print(f"{command=} finishe with:\n{result}")

    return result


async def login(registry: str, username: str, password: SecretStr, debug: bool) -> None:
    await _execute_command(
        [
            "crane",
            "auth",
            "login",
            registry,
            "--username",
            username,
            "--password",
            password,
        ],
        debug=debug,
    )


async def digest(image: str, debug: bool) -> str:
    return await _execute_command(["crane", "digest", image], debug=debug)


async def copy(source_image: str, destination_image: str, debug: bool) -> None:
    await _execute_command(
        ["crane", "copy", source_image, destination_image], debug=debug
    )
