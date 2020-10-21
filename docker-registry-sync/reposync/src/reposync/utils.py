import asyncio

from typing import Tuple


async def run_command_in_shell(command: str) -> Tuple[int, str]:
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    decoded_stdout = stdout.decode()
    decoded_stderr = stderr.decode()

    result = (
        decoded_stdout
        if len(decoded_stderr) == 0
        else f"{decoded_stdout}❌{decoded_stderr}"
    )

    return process.returncode, result
