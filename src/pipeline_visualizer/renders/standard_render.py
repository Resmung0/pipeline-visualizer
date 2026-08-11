"""Render pipeline stages using rich panels and arrows."""

import shlex
from collections.abc import Iterator
from itertools import count

from loguru import logger
from rich.console import Console, RenderableType
from rich.measure import Measurement
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pipeline_visualizer.constants import (
    ARROW_STYLE_COLOR,
    CELL_ACCENT_MUTED,
    CELL_BACKGROUND,
    CELL_DIM,
    CELL_GLOW,
    CELL_TEXT,
)
from pipeline_visualizer.enums import (
    Operator,
)
from pipeline_visualizer.models import Pipeline, Stage
from pipeline_visualizer.types import ArrowStyle, TitlePosition

console = Console(color_system="truecolor")


def __set_title(
    position: TitlePosition, stage_id: int, content: Text
) -> tuple[Text | None, Text | None, int | None, bool]:
    stage_title_text = Text(f"Stage {stage_id + 1}", style=f"bold {CELL_DIM}")

    title: Text | None = None
    subtitle: Text | None = None
    expand = False
    width: int | None = None

    if position == "bottom":
        stage_title_str = f"Stage {stage_id + 1}"
        measurement = Measurement.get(console, console.options, content)
        if measurement and measurement.maximum is not None:
            content_width = measurement.maximum

        width = max(content_width + 4, len(stage_title_str) + 6)
        subtitle = stage_title_text
        expand = True
    else:
        title = stage_title_text

    return title, subtitle, width, expand


def _render_stage(stage: Stage, stage_id: int, title_position: TitlePosition) -> Panel:
    command = " ".join(
        part for part in (stage.command, stage.subcommand, stage.parameter) if part
    )
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not command:
        tokens = [command]

    executable, *args = tokens
    content = Text(executable, style=f"bold {CELL_ACCENT_MUTED}")
    if args:
        content.append("\n")
        content.append(" ".join(args), style=f"bold {CELL_TEXT}")

    title, subtitle, width, expand = __set_title(title_position, stage_id, content)

    return Panel(
        content,
        title=title,
        subtitle=subtitle,
        border_style=CELL_GLOW,
        padding=(0, 1),
        style=f"on {CELL_BACKGROUND}",
        expand=expand,
        width=width,
    )


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
    node: Pipeline,
    arrow_style: ArrowStyle,
    stage_counter: Iterator[int],
    title_position: TitlePosition,
) -> Table:
    left = node.left
    if not isinstance(left, Pipeline):
        raise TypeError("OR branch alignment requires a pipeline on the left side.")

    left_stage = _render_node(left.left, arrow_style, stage_counter, title_position)
    and_stage = _render_node(left.right, arrow_style, stage_counter, title_position)
    or_stage = _render_node(node.right, arrow_style, stage_counter, title_position)
    and_connector = left.delimiter.arrow_style(arrow_style)
    or_connector = node.delimiter.arrow_style(arrow_style)

    return _render_branch_alignment(
        left_stage,
        and_connector,
        and_stage,
        or_connector,
        or_stage,
    )


def _render_node(
    node: Stage | Pipeline,
    arrow_style: ArrowStyle,
    stage_counter: Iterator[int],
    title_position: TitlePosition,
) -> RenderableType:
    if isinstance(node, Stage):
        return _render_stage(node, next(stage_counter), title_position)

    if (
        node.delimiter == Operator.OR
        and isinstance(node.left, Pipeline)
        and node.left.delimiter == Operator.AND
    ):
        return _render_or_below_and(node, arrow_style, stage_counter, title_position)

    rendered_children = [
        _render_node(node.left, arrow_style, stage_counter, title_position),
        _render_node(node.right, arrow_style, stage_counter, title_position),
    ]
    connector = node.delimiter.arrow_style(arrow_style)
    if node.delimiter.is_horizontal():
        return _render_horizontal(rendered_children, connector)

    return _render_vertical(rendered_children, connector)


@logger.catch
def render(
    node: Stage | Pipeline,
    arrow_style: ArrowStyle,
    title_position: TitlePosition,
) -> None:
    """Render a pipeline with the specified stages and arrow style.

    Args:
        node (Stage | Pipeline): The pipeline structure containing stages to render.
        arrow_style (ArrowStyle): The arrow style configuration for connecting stages.
        title_position (TitlePosition): The position of the stage title ("top" or "bottom").
    """
    rendered_node = _render_node(node, arrow_style, count(), title_position)
    console.print(rendered_node)
