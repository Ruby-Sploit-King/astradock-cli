import inspect

from astradock import workspace


def test_workspace_does_not_use_shell_execution() -> None:
    source = inspect.getsource(workspace)

    assert "shell=True" not in source
