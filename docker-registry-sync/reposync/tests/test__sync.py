from reposync._sync import _get_registry_image
from reposync._models import RegistryImage, DockerImage, DockerTag
import pytest


@pytest.mark.parametrize(
    "url,image,tag,expected",
    [
        pytest.param("some_repo", "a/path", None, "some_repo/a/path"),
        pytest.param("some_repo", "/a/path", None, "some_repo/a/path"),
        pytest.param("some_repo", "a/path", "tag", "some_repo/a/path:tag"),
        pytest.param("some_repo", "/a/path", "tag", "some_repo/a/path:tag"),
    ],
)
def test__get_registry_image(
    url: str, image: DockerImage, tag: DockerTag | None, expected: RegistryImage
):
    assert _get_registry_image(url=url, image=image, tag=tag) == expected
