"""AstraDock CLI entry point: organize local development projects."""

from __future__ import annotations

import json
import logging
import signal
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from astradock.models import ProjectRecord
from astradock.registry import ProjectRegistry
from astradock.workspace import inspect_project

app = typer.Typer(
    name="astradock",
    help="A neon terminal workspace catalog for developers.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)

console = Console()
errors = Console(stderr=True)


def configure_logging(verbose: bool) -> None:
    """Send diagnostic messages to stderr without cluttering normal output."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )


def render_projects(projects: list[ProjectRecord]) -> None:
    """Render the saved workspace catalog as a terminal table."""
    if not projects:
        console.print(
            Panel(
                "[yellow]Your dock is empty.[/yellow]\n"
                "Add a project with "
                "[bold cyan]astradock add alias /path/to/project[/bold cyan].",
                title="ASTRADOCK // WORKSPACE",
                border_style="bright_blue",
            )
        )
        return

    table = Table(
        title="ASTRADOCK // WORKSPACE DOCK",
        border_style="bright_blue",
    )
    table.add_column("ALIAS", style="bold cyan")
    table.add_column("PROJECT")
    table.add_column("LANGUAGE", style="magenta")
    table.add_column("PATH", overflow="fold")
    table.add_column("GIT", style="green")

    for project in projects:
        table.add_row(
            project.alias,
            project.name,
            project.language or "—",
            str(project.path),
            "● tracked" if project.is_git else "○ no Git",
        )

    console.print(table)


def handle_shutdown(signum: int, _frame: object) -> None:
    """Turn a termination signal into a clean CLI interruption."""
    raise KeyboardInterrupt(f"Signal {signum}")


@app.callback()
def common_options(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show diagnostic logs."),
    ] = False,
) -> None:
    """Configure common CLI behavior."""
    configure_logging(verbose)


@app.command()
def add(
    alias: Annotated[
        str,
        typer.Argument(help="Short unique name for this project."),
    ],
    path: Annotated[
        Path,
        typer.Argument(help="Path to the project directory."),
    ],
) -> None:
    """Register a local project in your workspace dock."""
    try:
        record = inspect_project(alias, path)

        with ProjectRegistry() as registry:
            registry.add(record)

    except (OSError, ValueError, RuntimeError) as exc:
        logging.error("%s", exc)
        raise typer.Exit(code=2) from exc

    console.print(
        Panel(
            f"[bold green]✓ Project docked[/bold green]\n"
            f"Alias: [cyan]{record.alias}[/cyan]\n"
            f"Path: {record.path}\n"
            f"Language: {record.language or 'Unknown'}",
            title="ASTRADOCK // SUCCESS",
            border_style="green",
        )
    )


@app.command("list")
def list_projects() -> None:
    """List registered projects."""
    with ProjectRegistry() as registry:
        render_projects(registry.list_all())


@app.command()
def inspect(
    alias: Annotated[
        str,
        typer.Argument(help="Alias of a registered project."),
    ],
) -> None:
    """Show live filesystem and Git details for a registered project."""
    with ProjectRegistry() as registry:
        project = registry.get(alias)

    if project is None:
        errors.print(f"[red]Unknown project alias:[/red] {alias}")
        raise typer.Exit(code=2)

    live = inspect_project(project.alias, project.path)

    console.print(
        Panel(
            f"[bold cyan]{live.name}[/bold cyan]\n"
            f"Alias: [white]{live.alias}[/white]\n"
            f"Path: {live.path}\n"
            f"Language: {live.language or 'Unknown'}\n"
            f"Python files: {live.python_files}\n"
            f"Git: {live.git_summary or 'Not a Git repository'}",
            title="ASTRADOCK // PROJECT INSPECTOR",
            border_style="magenta",
        )
    )


@app.command()
def remove(
    alias: Annotated[
        str,
        typer.Argument(help="Alias to remove from the catalog."),
    ],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip the confirmation prompt."),
    ] = False,
) -> None:
    """Remove a project from the catalog without deleting its files."""
    if not yes and not typer.confirm(
        f"Remove '{alias}' from AstraDock? Project files stay untouched."
    ):
        raise typer.Abort()

    with ProjectRegistry() as registry:
        removed = registry.remove(alias)

    if not removed:
        errors.print(f"[red]Unknown project alias:[/red] {alias}")
        raise typer.Exit(code=2)

    console.print(
        f"[green]✓ Removed {alias} from the dock. Files were not deleted.[/green]"
    )


@app.command()
def export(
    output: Annotated[
        Path,
        typer.Argument(help="Destination JSON file."),
    ] = Path("astradock-export.json"),
) -> None:
    """Export the registered project catalog to JSON."""
    with ProjectRegistry() as registry:
        projects = registry.list_all()

    destination = output.expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = [project.to_dict() for project in projects]
    destination.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    console.print(
        f"[green]✓ Exported {len(payload)} projects to {destination}[/green]"
    )


def main() -> None:
    """Register graceful shutdown behavior and run the CLI."""
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        app()
    except KeyboardInterrupt:
        errors.print("\n[yellow]Shutdown requested.[/yellow]")
        raise SystemExit(130) from None


if __name__ == "__main__":
    main()
