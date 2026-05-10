from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.pipeline_visualizer.enums import Arrows

console = Console()


def render(stages: list[list[str]], arrows: Arrows) -> None:
    items = []
    for i, tokens in enumerate(stages):
        comando = tokens[0]
        args = " ".join(tokens[1:])

        conteudo = f"[bold cyan]{comando}[/]"
        if args:
            conteudo += f"\n[dim]{args}[/]"

        items.append(Panel(conteudo, title=f"[dim]Stage {i + 1}[/]", expand=False))

        if i < len(stages) - 1:
            items.append(Text(arrows.symbol, style="bold yellow"))

    table = Table.grid(padding=(0, 1))
    for i in range(len(items)):
        # Panel columns go at the top, arrow columns in the middle
        vertical = "middle" if i % 2 == 1 else "top"
        table.add_column(vertical=vertical)
    table.add_row(*items)
    console.print(table)
