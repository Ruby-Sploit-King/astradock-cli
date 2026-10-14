from pathlib import Path

import pytest

from astradock.models import ProjectRecord
from astradock.registry import ProjectRegistry


def make_project(alias: str, path: Path) -> ProjectRecord:
    return ProjectRecord(
        alias,
        path.name,
        path,
        "Python",
        2,
        False,
    )


def test_registry_add_get_list_remove(tmp_path: Path) -> None:
    project_path = tmp_path / "demo"
    project_path.mkdir()

    with ProjectRegistry(tmp_path / "registry.sqlite3") as registry:
        registry.add(make_project("demo", project_path))

        stored = registry.get("demo")
        assert stored is not None
        assert stored.name == "demo"
        assert len(registry.list_all()) == 1
        assert registry.remove("demo") is True
        assert registry.get("demo") is None


def test_duplicate_alias_is_rejected(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()

    with ProjectRegistry(tmp_path / "registry.sqlite3") as registry:
        registry.add(make_project("same", first))

        with pytest.raises(ValueError, match="already registered"):
            registry.add(make_project("same", second))
