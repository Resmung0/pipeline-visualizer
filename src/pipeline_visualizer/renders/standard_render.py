"""Render pipeline stages using rich panels and arrows."""

import shlex
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from itertools import count

from loguru import logger
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pipeline_visualizer.constants import ARROW_STYLE_COLOR
from pipeline_visualizer.enums import (
    DiagonalArrow,
    HorizontalArrow,
    Operator,
    Redirect,
    VerticalArrow,
)
from pipeline_visualizer.models import Pipeline, Stage
from pipeline_visualizer.types import ArrowStyle

console = Console()



@dataclass(frozen=True)
class ConnectorConfig:
    """Configuration for rendering a delimiter connector."""

    arrow_factory: Callable[[ArrowStyle], str]
    horizontal: bool


DELIMITER_RENDER_CONFIG: dict[Operator | Redirect, ConnectorConfig] = {
    Operator.PIPE: ConnectorConfig(
        lambda style: VerticalArrow[style.upper()], horizontal=False
    ),
    Operator.AND: ConnectorConfig(
        lambda style: HorizontalArrow[style.upper()], horizontal=True
    ),
    Operator.OR: ConnectorConfig(
        lambda style: DiagonalArrow[style.upper()], horizontal=True
    ),
    Operator.SEMICOLON: ConnectorConfig(
        lambda style: HorizontalArrow[style.upper()], horizontal=True
    ),
    Redirect.OUT: ConnectorConfig(lambda _style: Redirect.OUT.value, horizontal=False),
    Redirect.OUT_APPEND: ConnectorConfig(
        lambda _style: Redirect.OUT_APPEND.value, horizontal=False
    ),
    Redirect.IN: ConnectorConfig(lambda _style: Redirect.IN.value, horizontal=False),
    Redirect.IN_APPEND: ConnectorConfig(
        lambda _style: Redirect.IN_APPEND.value, horizontal=False
    ),
}

# Ensure all supported delimiters are configured
for delimiter in list(Operator) + list(Redirect):
    if delimiter not in DELIMITER_RENDER_CONFIG:
        raise RuntimeError(f"Delimiter {delimiter} is missing from DELIMITER_RENDER_CONFIG")



def _stage_command(stage: Stage) -> str:
    return " ".join(
        part for part in (stage.command, stage.subcommand, stage.parameter) if part
    )


def _split_command(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def _render_stage(stage: Stage, stage_id: int) -> Panel:
    command = _stage_command(stage)
    tokens = _split_command(command) or [command]
    executable, *args = tokens

    content = Text(executable, style="bold cyan")
    if args:
        content.append("\n")
        content.append(" ".join(args), style="dim")

    return Panel(content, title=f"[dim]Stage {stage_id + 1}[/]", expand=False)


def _choose_connector(delimiter: Operator | Redirect, arrow_style: ArrowStyle) -> str:
    try:
        config = DELIMITER_RENDER_CONFIG[delimiter]
    except KeyError:
        raise RuntimeError(f"Delimiter {delimiter} unsupported!") from None
    return config.arrow_factory(arrow_style)


def _render_horizontal(stages: list[RenderableType], connector: str) -> Table:
    # Create a list of panels and arrows to be added to the table.
    # Each stage is followed by a connector, except for the last stage.
    panels: list[RenderableType] = []
    for stage_id, stage in enumerate(stages, start=1):
        panels.append(stage)
        if stage_id < len(stages):
            panels.append(Text(connector, style=ARROW_STYLE_COLOR))

    # Create a table with the appropriate number of columns for the panels and arrows.
    table = Table.grid(padding=(0, 1))
    for panel_id in range(len(panels)):
        # Panel columns go at the top, arrow columns in the middle
        table.add_column(
            vertical="middle" if panel_id % 2 == 1 else "top", justify="center"
        )
    table.add_row(*panels)
    return table


def _render_vertical(stages: list[RenderableType], connector: str) -> Table:
    table = Table.grid(padding=(0, 0))
    table.add_column(justify="center")

    for stage_id, stage in enumerate(stages, start=1):
        table.add_row(stage)
        if stage_id < len(stages):
            table.add_row(Text(connector, style=ARROW_STYLE_COLOR))

    return table


def _render_branch_alignment(
    left_stage: RenderableType,
    left_connector: str,
    right_stage_top: RenderableType,
    right_connector: str,
    right_stage_bottom: RenderableType,
) -> Table:
    blank = Text("")
    table = Table.grid(padding=(0, 1))
    table.add_column(vertical="top", justify="center")
    table.add_column(vertical="middle", justify="center")
    table.add_column(vertical="top", justify="center")

    table.add_row(
        left_stage, Text(left_connector, style=ARROW_STYLE_COLOR), right_stage_top
    )
    table.add_row(blank, Text(right_connector, style=ARROW_STYLE_COLOR), blank)
    table.add_row(blank, blank, right_stage_bottom)
    return table


def _render_or_below_and(
    node: Pipeline, arrow_style: ArrowStyle, stage_counter: Iterator[int]
) -> Table:
    left = node.left
    if not isinstance(left, Pipeline):
        raise TypeError("OR branch alignment requires a pipeline on the left side.")

    left_stage = _render_node(left.left, arrow_style, stage_counter)
    and_stage = _render_node(left.right, arrow_style, stage_counter)
    or_stage = _render_node(node.right, arrow_style, stage_counter)
    and_connector = _choose_connector(left.delimiter, arrow_style)
    or_connector = _choose_connector(node.delimiter, arrow_style)

    return _render_branch_alignment(
        left_stage,
        and_connector,
        and_stage,
        or_connector,
        or_stage,
    )


def _is_horizontal(delimiter: Operator | Redirect) -> bool:
    try:
        return DELIMITER_RENDER_CONFIG[delimiter].horizontal
    except KeyError:
        raise RuntimeError(f"Delimiter {delimiter} unsupported!") from None


def _render_node(
    node: Stage | Pipeline, arrow_style: ArrowStyle, stage_counter: Iterator[int]
) -> RenderableType:
    if isinstance(node, Stage):
        return _render_stage(node, next(stage_counter))

    if (
        node.delimiter == Operator.OR
        and isinstance(node.left, Pipeline)
        and node.left.delimiter == Operator.AND
    ):
        return _render_or_below_and(node, arrow_style, stage_counter)

    rendered_children = [
        _render_node(node.left, arrow_style, stage_counter),
        _render_node(node.right, arrow_style, stage_counter),
    ]
    connector = _choose_connector(node.delimiter, arrow_style)

    if _is_horizontal(node.delimiter):
        return _render_horizontal(rendered_children, connector)

    return _render_vertical(rendered_children, connector)


@logger.catch
def render(stages: Stage | Pipeline, arrow_style: ArrowStyle) -> None:
    """Render a pipeline with the specified stages and arrow style.

    Args:
        stages (Stage | Pipeline): The pipeline structure containing stages to render.
        arrow_style (ArrowStyle): The arrow style configuration for connecting stages.
    """
    rendered_node = _render_node(stages, arrow_style, count())
    console.print(rendered_node)
