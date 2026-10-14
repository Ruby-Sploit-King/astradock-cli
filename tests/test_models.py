from pathlib import Path

from astradock.models import ProjectRecord


def test_project_record_exports_path_as_string() -> None:
    record = ProjectRecord(
        "demo",
        "demo-app",
        Path("/tmp/demo"),
        "Python",
        3,
        True,
        "clean",
    )

    assert record.to_dict()["path"] == "/tmp/demo"
    assert record.to_dict()["python_files"] == 3
