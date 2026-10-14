# AstraDock CLI

AstraDock is a neon-styled terminal workspace catalog for developers.
Register local coding projects under short aliases, inspect project metadata
and Git status, keep a persistent SQLite registry, and export the catalog
to JSON.

## Features

- Rich terminal tables and styled status output.
- Unique aliases for local project directories.
- Language detection for Python, Go, Rust, C/C++, JavaScript/TypeScript,
  Java, and C#.
- Python source counting while ignoring virtual environments and generated
  folders.
- Git branch and working-tree status using safe argument-list subprocess calls.
- SQLite persistence at `~/.local/share/astradock/projects.sqlite3`.
- JSON export, pytest tests, Ruff, mypy, and GitHub Actions CI.
- Removing an alias never deletes project files.

## Requirements

Python 3.11+ and Git for Git status inspection.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
