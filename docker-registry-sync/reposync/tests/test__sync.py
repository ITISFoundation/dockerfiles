from reposync._sync import _get_image
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
def test_something(
    url: str, image: DockerImage, tag: DockerTag | None, expected: RegistryImage
):
    assert _get_image(url=url, image=image, tag=tag) == expected
