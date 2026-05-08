from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()


def render(stages: list[list[str]]) -> None:
    items = []
    for i, tokens in enumerate(stages):
        comando = tokens[0]
        args = " ".join(tokens[1:])

        conteudo = f"[bold cyan]{comando}[/]"
        if args:
            conteudo += f"\n[dim]{args}[/]"

        items.append(Panel(conteudo, title=f"[dim]Etapa {i+1}[/]", expand=False))

        if i < len(stages) - 1:
            items.append(Text(" ──► ", style="bold yellow"))

    table = Table.grid(padding=(0, 1))

    for i in range(len(items)):
        # colunas dos painéis ficam no topo, colunas das setas no meio
        vertical = "middle" if i % 2 == 1 else "top"
        table.add_column(vertical=vertical)

    table.add_row(*items)
    console.print(table)
