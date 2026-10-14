import sqlite3
from pathlib import Path

from astradock.models import ProjectRecord

DEFAULT_DATABASE = (
    Path.home() / ".local" / "share" / "astradock" / "project.sqlite3"
)

class ProjectRegistry:
    def __init__(self, database: Path = DEFAULT_DATABASE) -> None:
        self.database = database
        self.connection: sqlite3.Connection | None = None

    def __enter__(self) -> "ProjectRegistry":
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database)
        self.connection.row_factory = sqlite3.Row

        self.connection.execute(
            """
             CREATE TABLE IF NOT EXISTS projects (
                alias TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                language TEXT,
                python_files INTEGER NOT NULL,
                is_git INTEGER NOT NULL,
                git_summary TEXT
            )
            """
        )
        self.connection.commit()
        return self 

    def __exit__(self, *_exc: object) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None 

    def add(self, project: ProjectRecord) -> None:
        try:
            self._connection().execute(
                """
                INSERT INTO projects
                    (alias, name, path, language, python_files, is_git, git_summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.alias,
                    project.name,
                    str(project.path),
                    project.language,
                    project.python_files,
                    int(project.is_git),
                    project.git_summary,
                ),
            )
            self._connection().commit()

        except sqlite3.IntegrityError as exc:
            raise ValueError(
                "That alias or project path is already registered."
            ) from exc

    def list_all(self) -> list[ProjectRecord]:
        """Return all registered projects ordered by alias."""
        rows = self._connection().execute(
            "SELECT * FROM projects ORDER BY alias COLLATE NOCASE"
        ).fetchall()

        return [self._from_row(row) for row in rows]

    def get(self, alias: str) -> ProjectRecord | None:
        """Find a project by its exact alias."""
        row = self._connection().execute(
            "SELECT * FROM projects WHERE alias = ?",
            (alias,),
        ).fetchone()

        return self._from_row(row) if row else None

    def remove(self, alias: str) -> bool:
        """Remove a catalog entry without touching project files."""
        cursor = self._connection().execute(
            "DELETE FROM projects WHERE alias = ?",
            (alias,),
        )
        self._connection().commit()
        return cursor.rowcount > 0

    def _connection(self) -> sqlite3.Connection:
        """Require the registry to be used within its context manager."""
        if self.connection is None:
            raise RuntimeError("Use ProjectRegistry inside a with block.")
        return self.connection

    @staticmethod
    def _from_row(row: sqlite3.Row) -> ProjectRecord:
        """Convert one SQLite row into a typed project record."""
        return ProjectRecord(
            alias=row["alias"],
            name=row["name"],
            path=Path(row["path"]),
            language=row["language"],
            python_files=row["python_files"],
            is_git=bool(row["is_git"]),
            git_summary=row["git_summary"],
        )
