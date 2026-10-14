import re
import subprocess
from pathlib import Path

from astradock.models import ProjectRecord

ALIAS_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,31}$")

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
}

LANGUAGE_MARKERS = {
    "Python": ("pyproject.toml", "requirements.txt", "setup.py"),
    "Go": ("go.mod",),
     "Rust": ("Cargo.toml",),
    "C/C++": ("CMakeLists.txt", "Makefile"),
    "JavaScript/TypeScript": ("package.json",),
    "Java": ("pom.xml", "build.gradle", "build.gradle.kts"),
    "C#": ("*.csproj", "*.sln"),
}

def validate_alias(alias: str) -> str:
    normalized = alias.strip()
    if not ALIAS_PATTERN.fullmatch(normalized):
        raise ValueError("Alias must be 1-32 letters, digits, underscores, or hyphens")
    return normalized

def detect_language(root: Path) -> str | None:
    for language, markers in LANGUAGE_MARKERS.items():
        if any(list(root.glob(marker)) for marker in markers):
            return language 

    if list(root.glob("*.py")):
        return "Python"
    if list(root.glob("*.go")):
        return "Golang"
    if list(root.glob("*.rs")):
        return "Rust"

    return None 

def count_python_files(root: Path) -> int:
    return sum(1 for path in root.rglob("*.py")
    if not any(part in IGNORED_DIRS for part in path.parts))

def git_summary(root: Path) -> tuple[bool, str | None]:
    try:
        branch = subprocess.run(
            ["git", "-C", str(root), "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
            timeout=3,
        ).stdout.strip()

        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
            timeout=3,
        ).stdout

    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return False, None

    state = "clean" if not status else f"{len(status.splitlines())} changed item(s)"
    return True, f"branch {branch or '(detached HEAD)'} · {state}"


def inspect_project(alias: str, path: Path) -> ProjectRecord:
    """Validate a directory and collect its current project metadata."""
    safe_alias = validate_alias(alias)
    root = path.expanduser().resolve()

    if not root.exists():
        raise ValueError(f"Project path does not exist: {root}")

    if not root.is_dir():
        raise ValueError(f"Project path is not a directory: {root}")

    is_git, summary = git_summary(root)

    return ProjectRecord(
        alias=safe_alias,
        name=root.name or str(root),
        path=root,
        language=detect_language(root),
        python_files=count_python_files(root),
        is_git=is_git,
        git_summary=summary,
    )
