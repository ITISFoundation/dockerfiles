import asyncio
import json

from typing import Tuple, Dict, List, Set

from .exceptions import SkopeoException
from .utils import run_command_in_shell


def _bool_format(bool_value: bool) -> str:
    return str(bool_value).lower()


async def skopeo_command_wrapper(command: str, json_decode_output=True) -> Dict:
    """Runs a command and returns the result as json or an raises an error"""
    print(f"✨ Running '{command}'")
    exit_code, output = await run_command_in_shell(command)
    if exit_code != 0:
        print(f"❌Error while running: '{command}', see below:\n{output}")
        raise SkopeoException(f"Had an error while running '{command}'")

    return json.loads(output) if json_decode_output else output


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


async def _skopeo_inspect(image: str, tls_verify: bool = True) -> Dict:
    command = f"skopeo inspect --tls-verify={_bool_format(tls_verify)} docker://{image}"
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
    return await skopeo_command_wrapper(command, False)


async def skopeo_delete_image(image_with_tag: str, tls_verify: bool = True):
    """Remove an image from a target registry"""
    if ":" not in image_with_tag:
        raise ValueError(f"Provided image '{image_with_tag}' dose not contain a tag")
    command = (
        "skopeo delete "
        f"--tls-verify={_bool_format(tls_verify)} "
        f"docker://{image_with_tag}"
    )
    try:
        await skopeo_command_wrapper(command, False)
    except SkopeoException:
        print(f"🚨Could not remove image {image_with_tag}")


async def get_image_tags_for_image(image: str, tls_verify: bool = True):
    """Returns all the image tags in target repository"""
    result = await _skopeo_inspect(image, tls_verify)
    return result["RepoTags"]


async def get_images_to_remove(
    base_image: str, tags_to_keep: List[str], tls_verify: bool = True
) -> Set[str]:
    """Given a repository will returns the images to delete"""
    try:
        tags = set(await get_image_tags_for_image(base_image, tls_verify))
    except SkopeoException:
        print(f"Could not inspect {base_image}, no tags were removed")
        return {}

    set_tags_to_keep = set(tags_to_keep)

    tags_to_remove = tags - set_tags_to_keep
    kept_after_removal = tags - tags_to_remove

    if len(kept_after_removal) < len(tags_to_keep):
        raise ValueError(
            f"The registry will end up with '{kept_after_removal}'"
            f", was also expecting {set_tags_to_keep}'"
        )
    return {f"{base_image}:{tag}" for tag in tags_to_remove}
