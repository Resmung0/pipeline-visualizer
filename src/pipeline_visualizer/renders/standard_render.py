from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def render(stages: list[list[str]]) -> None:
    items = []
    for i, tokens in enumerate(stages):
        command = tokens[0]
        args = " ".join(tokens[1:])

        content = f"[bold cyan]{command}[/]"
        if args:
            content += f"\n[dim]{args}[/]"
        items.append(Panel(content, title=f"[dim]Stage {i + 1}[/]", expand=False))

        if i < len(stages) - 1:
            items.append(Text("→", style="bold yellow", justify="center"))

    console.print(Columns(items, align="center", equal=False))
