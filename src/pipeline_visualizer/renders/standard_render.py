import shlex
from collections.abc import Iterator
from itertools import count
from typing import Literal, TypeAlias

from loguru import logger
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.pipeline_visualizer.enums import (
    ConditionalANDArrow,
    ConditionalORArrow,
    Delimiter,
    PipeArrow,
)
from src.pipeline_visualizer.types import Pipeline

ArrowStyle: TypeAlias = Literal["standard", "alternative", "thick"]
ArrowInput: TypeAlias = (
    ArrowStyle | PipeArrow | ConditionalORArrow | ConditionalANDArrow
)

console = Console()


def _parse_tokens(tokens: list[str], token_id: int) -> Panel:
    command = tokens[0]
    args = " ".join(tokens[1:])

    content = f"[bold cyan]{command}[/]"
    if args:
        content += f"\n[dim]{args}[/]"

    return Panel(content, title=f"[dim]Stage {token_id + 1}[/]", expand=False)


def _parse_command(command: str, token_id: int) -> Panel:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    return _parse_tokens(tokens or [command], token_id)


def _arrow_style(arrows: ArrowInput) -> ArrowStyle:
    if isinstance(
        arrows,
        (PipeArrow, ConditionalORArrow, ConditionalANDArrow),
    ):
        return arrows.value

    return arrows


def _arrow_for(
    delimiter: Delimiter,
    arrows: ArrowInput,
) -> PipeArrow | ConditionalORArrow | ConditionalANDArrow:
    style = _arrow_style(arrows)

    if delimiter is Delimiter.PIPE:
        return PipeArrow(style)
    if delimiter is Delimiter.AND:
        return ConditionalANDArrow(style)
    if delimiter is Delimiter.OR and style == "alternative":
        return ConditionalORArrow.ALTERNATIVE

    return ConditionalORArrow.STANDARD


def _render_horizontal(
    stages: list[RenderableType],
    arrow: PipeArrow | ConditionalORArrow | ConditionalANDArrow,
) -> Table:
    panels: list[RenderableType] = []
    for stage_id, stage in enumerate(stages):
        panels.append(stage)
        if stage_id < len(stages) - 1:
            panels.append(Text(arrow.symbol, style="bold yellow"))

    table = Table.grid(padding=(0, 1))
    for panel_id in range(len(panels)):
        # Panel columns go at the top, arrow columns in the middle
        vertical = "middle" if panel_id % 2 == 1 else "top"
        table.add_column(vertical=vertical)
    table.add_row(*panels)
    return table


def _render_vertical(
    stages: list[RenderableType],
    arrow: PipeArrow | ConditionalORArrow | ConditionalANDArrow,
) -> Table:
    table = Table.grid(padding=(0, 0))
    table.add_column(justify="center")

    for stage_id, stage in enumerate(stages):
        table.add_row(stage)
        if stage_id < len(stages) - 1:
            table.add_row(Text(arrow.symbol, style="bold yellow"))

    return table


def _render_node(
    stage: str | Pipeline,
    arrows: ArrowInput,
    stage_counter: Iterator[int],
) -> RenderableType:
    if isinstance(stage, str):
        return _parse_command(stage, next(stage_counter))

    delimiter = stage["delimiter"]
    children = stage["stages"]
    if delimiter is None:
        if len(children) == 1:
            return _render_node(children[0], arrows, stage_counter)

        return _render_vertical(
            [_render_node(child, arrows, stage_counter) for child in children],
            ConditionalANDArrow.STANDARD,
        )

    rendered_children = [
        _render_node(child, arrows, stage_counter) for child in children
    ]
    arrow = _arrow_for(delimiter, arrows)
    if delimiter is Delimiter.PIPE:
        return _render_horizontal(rendered_children, arrow)

    return _render_vertical(rendered_children, arrow)


@logger.catch
def render(
    stages: Pipeline,
    arrows: ArrowInput,
) -> None:
    console.print(_render_node(stages, arrows, count()))
