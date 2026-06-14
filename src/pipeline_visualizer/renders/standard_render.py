"""Render pipeline stages using rich panels and arrows."""

import shlex
from collections.abc import Iterator
from itertools import count

from loguru import logger
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pipeline_visualizer.enums import (
    ConditionalANDArrow,
    ConditionalORArrow,
    Operator,
    PipeArrow,
    Redirect,
)
from pipeline_visualizer.models import Pipeline
from pipeline_visualizer.types import ArrowInput, ArrowStyle

console = Console()


def _extract_command(command: str, token_id: int) -> Panel:
    def extract_tokens(tokens: list[str], token_id: int) -> Panel:
        command = tokens[0]
        args = " ".join(tokens[1:])

        content = f"[bold cyan]{command}[/]"
        if args:
            content += f"\n[dim]{args}[/]"

        return Panel(content, title=f"[dim]Stage {token_id + 1}[/]", expand=False)

    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    return extract_tokens(tokens or [command], token_id)


def _choose_arrow(
    delimiter: Operator | Redirect, arrow: ArrowStyle | str
) -> ArrowInput:
    # `arrows` can be passed as an enum member or as a plain string
    # (e.g. from CLI). Normalize to a string style when necessary.
    if isinstance(delimiter, Redirect):
        raise RuntimeError("Redirect is not implemented yet!")

    style = arrow.value if hasattr(arrow, "value") else arrow
    match delimiter:
        case Operator.PIPE:
            chosed_arrow = PipeArrow(style)
        case Operator.AND:
            chosed_arrow = ConditionalANDArrow(style)
        case Operator.OR:
            chosed_arrow = ConditionalORArrow(style)
        case _:
            raise RuntimeError(f"Operator {delimiter} unsupported!")

    return chosed_arrow


def _render_horizontal(stages: list[RenderableType], arrow: ArrowInput) -> Table:
    panels: list[RenderableType] = []
    for stage_id, stage in enumerate(stages):
        panels.append(stage)
        if stage_id < len(stages) - 1:
            panels.append(Text(arrow.symbol, style=arrow.color))

    table = Table.grid(padding=(0, 1))
    for panel_id in range(len(panels)):
        # Panel columns go at the top, arrow columns in the middle
        vertical = "middle" if panel_id % 2 == 1 else "top"
        table.add_column(vertical=vertical)
    table.add_row(*panels)
    return table


def _render_horizontal(stages: list[RenderableType], arrow: ArrowInput) -> Table:
    panels: list[RenderableType] = []
    for stage_id, stage in enumerate(stages):
        panels.append(stage)
        if stage_id < len(stages) - 1:
            panels.append(Text(arrow.symbol, style=arrow.color))

    table = Table.grid(padding=(0, 1))
    for panel_id in range(len(panels)):
        # Panel columns go at the top, arrow columns in the middle
        vertical = "middle" if panel_id % 2 == 1 else "top"
        table.add_column(vertical=vertical, justify="center")
    table.add_row(*panels)
    return table


def _render_vertical(stages: list[RenderableType], arrow: ArrowInput) -> Table:
    table = Table.grid(padding=(0, 0))
    table.add_column(justify="center")

    for stage_id, stage in enumerate(stages):
        table.add_row(stage)
        if stage_id < len(stages) - 1:
            table.add_row(Text(arrow.symbol, style=arrow.color))

    return table


def _render_node(
    stage: str | Pipeline, arrow: ArrowStyle, stage_counter: Iterator[int]
) -> RenderableType:
    if isinstance(stage, str):
        return _extract_command(stage, next(stage_counter))

    delimiter = stage["delimiter"]
    children = stage["stages"]
    if delimiter is None:
        if len(children) == 1:
            return _render_node(children[0], arrow, stage_counter)

        return _render_vertical(
            [_render_node(child, arrow, stage_counter) for child in children],
            ConditionalANDArrow.STANDARD,
        )

    rendered_children = [
        _render_node(child, arrow, stage_counter) for child in children
    ]

    chosen_arrow = _choose_arrow(delimiter, arrow)
    if delimiter == Operator.PIPE:
        return _render_horizontal(rendered_children, chosen_arrow)

    return _render_vertical(rendered_children, chosen_arrow)


@logger.catch
def render(stages: Pipeline, arrow: ArrowStyle) -> None:
    """Render a pipeline with the specified stages and arrow style.

    Args:
        stages: The pipeline structure containing stages to render.
        arrow: The arrow style configuration for connecting stages.
    """
    rendered_node = _render_node(stages, arrow, count())
    console.print(rendered_node)
