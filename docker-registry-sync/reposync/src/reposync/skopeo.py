import asyncio

from typing import Tuple


async def run_command_in_shell(command: str) -> Tuple[int, str]:
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, _ = await process.communicate()
    result = stdout.decode()

    return process.returncode, result


async def sync_image():
    """Sync an image from a target registry to a destination registry """


async def delete_image():
    """Remove an image from a target registry"""


async def get_image_tags_for_image():
    """Returns all the image tags in target repository"""


async def get_images_to_remove():
    """Given a repository will returns the images to delete"""
