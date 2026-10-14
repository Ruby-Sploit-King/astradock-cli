from pathlib import Path

import pytest

from astradock.workspace import (
    count_python_files,
    detect_language,
    inspect_project,
    validate_alias,
)


def test_alias_validation() -> None:
    assert validate_alias("my-app_2") == "my-app_2"

    with pytest.raises(ValueError):
        validate_alias("../unsafe")


def test_project_inspection_detects_python(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='demo'\n",
        encoding="utf-8",
    )
    (tmp_path / "main.py").write_text(
        "print('hello')\n",
        encoding="utf-8",
    )

    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "hidden.py").write_text(
        "",
        encoding="utf-8",
    )

    record = inspect_project("demo", tmp_path)

    assert record.language == "Python"
    assert record.python_files == 1
    assert count_python_files(tmp_path) == 1


def test_unknown_language(tmp_path: Path) -> None:
    assert detect_language(tmp_path) is None


def test_missing_directory_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        inspect_project("missing", tmp_path / "missing")
