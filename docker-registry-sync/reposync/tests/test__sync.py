from pathlib import Path

from reposync._sync import (
    CopyResult,
    _RunStats,
    _get_registry_image,
    _write_tracebacks_file,
)
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


def test__run_stats_format_sorts_task_ids(tmp_path: Path):
    stats = _RunStats()
    stats.update(
        [
            ("z-task", CopyResult.COPIED),
            ("a-task", CopyResult.COPIED),
            ("m-task", CopyResult.SAME_DIGEST),
            ("y-fail", RuntimeError("boom")),
            ("b-fail", ValueError("nope")),
        ]
    )

    output = stats.format(tracebacks_file=tmp_path / "tb.txt")

    assert "total=5" in output
    assert "copied=2" in output
    assert "same-digest=1" in output
    assert "failed=2" in output
    # Copied + failed sections list task_ids only, sorted alphabetically.
    assert output.index("a-task") < output.index("z-task")
    assert output.index("b-fail") < output.index("y-fail")
    # No exception text leaks into the summary.
    assert "boom" not in output
    assert "nope" not in output
    # Trailer points at the tracebacks file.
    assert f"Tracebacks written to: {tmp_path / 'tb.txt'}" in output


def test__write_tracebacks_file_sorted_with_anchors(tmp_path: Path):
    target = tmp_path / "nested" / "tb.txt"
    failures: list[tuple[str, BaseException]] = [
        ("z-task", RuntimeError("zzz")),
        ("a-task", ValueError("aaa")),
    ]

    _write_tracebacks_file(target, failures)

    assert target.exists()
    content = target.read_text()
    assert "=== a-task ===" in content
    assert "=== z-task ===" in content
    # Sorted by task_id: a-task section comes before z-task section.
    assert content.index("=== a-task ===") < content.index("=== z-task ===")


def test__write_tracebacks_file_empty_on_no_failures(tmp_path: Path):
    target = tmp_path / "tb.txt"
    _write_tracebacks_file(target, [])
    assert target.exists()
    assert target.read_text() == ""


def test__run_stats_record_increments_live():
    stats = _RunStats()

    stats.record("a-task", CopyResult.COPIED)
    stats.record("b-task", CopyResult.SAME_DIGEST)
    stats.record("c-task", RuntimeError("boom"))

    assert stats.total == 3
    assert stats.copied == 1
    assert stats.same_digest == 1
    assert stats.failed == 1
    assert stats.copied_task_ids == ["a-task"]
    assert [tid for tid, _ in stats.failures] == ["c-task"]


def test__run_stats_progress_line():
    stats = _RunStats()
    stats.record("a-task", CopyResult.COPIED)
    stats.record("b-task", CopyResult.SAME_DIGEST)
    stats.record("c-task", RuntimeError("boom"))

    line = stats.progress_line(planned_total=10)

    assert "copied=1" in line
    assert "same-digest=1" in line
    assert "failed=1" in line
    assert "3/10" in line
    assert line.startswith("⏳")
