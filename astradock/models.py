from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass 
class ProjectRecord:
    alias: str 
    name: str 
    path: Path 
    language: str | None 
    python_files: int 
    is_git: bool 
    git_summary: str | None = None 

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data 
