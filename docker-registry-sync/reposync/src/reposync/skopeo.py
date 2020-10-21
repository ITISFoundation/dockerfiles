import asyncio
import json

from typing import Tuple, Dict

from .exceptions import SkopeoException
from .utils import run_command_in_shell


def _bool_format(bool_value: bool) -> str:
    return str(bool_value).lower()


async def skopeo_command_wrapper(command: str) -> Dict:
    """Runs a command and returns the result as json or an raises an error"""
    print(f"✨ Running '{command}'")
    exit_code, output = await run_command_in_shell(command)
    if exit_code != 0:
        print(f"❌Error while running: '{command}', see below:\n{output}")
        raise SkopeoException(f"Had an error while running '{command}'")

    return json.loads(output)


async def skopeo_login(registry: str, user: str, password: str, tls_verify: True):
    command = (
        f"skopeo login "
        f"--tls-verify={_bool_format(tls_verify)} "
        f"-u {user} -p {password} {registry}"
    )
    exit_code, output = await run_command_in_shell(command)
    if exit_code != 0:
        print(f"Error while trying to login\n{output}")
        raise SkopeoException(f"Could not locgin check above")


async def _skopeo_inspect(image: str) -> Dict:
    command = f"skopeo inspect docker://{image}"
    return await skopeo_command_wrapper(command)


async def skopeo_sync_image(
    source_image: str,
    destination_image: str,
    source_tls_verify: bool = True,
    destination_tls_verify: bool = True,
):
    """Sync an image from a target registry to a destination registry """
    command = (
        f"skopeo copy "
        f"--src-tls-verify={_bool_format(source_tls_verify)} "
        f"--dest-tls-verify={_bool_format(destination_tls_verify)} "
        f"docker://{source_image} docker://{destination_image}"
    )
    return await skopeo_command_wrapper(command)


async def skopeo_delete_image():
    """Remove an image from a target registry"""


async def get_image_tags_for_image(image: str):
    """Returns all the image tags in target repository"""
    result = await _skopeo_inspect(image)
    return result["RepoTags"]


async def get_images_to_remove():
    """Given a repository will returns the images to delete"""
