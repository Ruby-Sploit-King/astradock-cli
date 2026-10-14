"""Reusable terminal presentation helpers."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def render_banner() -> None:
    """Display the AstraDock identity banner."""
    title = Text()
    title.append(" ASTRA", style="bold bright_cyan")
    title.append("DOCK ", style="bold bright_magenta")
    title.append("// ", style="bright_white")
    title.append("DEV WORKSPACE CONTROL", style="bright_green")

    console.print(
        Panel(
            title,
            border_style="bright_blue",
            padding=(0, 2),
        )
    )


def render_message(message: str, success: bool = True) -> None:
    """Show a consistent success or warning message."""
    color = "green" if success else "yellow"
    icon = "✓" if success else "!"

    console.print(f"[bold {color}]{icon} {message}[/bold {color}]")


def render_error(message: str) -> None:
    """Show an error on stderr with a clear visual marker."""
    Console(stderr=True).print(
        Panel(
            f"[bold red]✗ {message}[/bold red]",
            border_style="red",
        )
    )
