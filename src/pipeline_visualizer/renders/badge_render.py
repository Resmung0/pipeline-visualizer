"""Render pipeline stages as Rich-styled badges."""

from collections.abc import Iterator
from itertools import count

from loguru import logger
from rich.console import Console, RenderableType
from rich.table import Table
from rich.text import Text

from pipeline_visualizer.constants import (
    ARROW_STYLE_COLOR,
    CELL_ACCENT,
    CELL_BACKGROUND,
    CELL_GLOW,
    CELL_TEXT,
)
from pipeline_visualizer.enums import Operator
from pipeline_visualizer.models import Pipeline, Stage
from pipeline_visualizer.types import ArrowStyle

console = Console(color_system="truecolor")


def _format_stage_label(stage: Stage) -> str:
    """Build a compact label for a stage badge.

    Args:
        stage (Stage): The stage to format.

    Returns:
        str: Space-joined command parts for the badge label.
    """
    return " ".join(
        part for part in (stage.command, stage.subcommand, stage.parameter) if part
    )


def _render_badge(stage: Stage, stage_id: int) -> Text:
    """Render a single stage as a numbered badge.

    The badge reuses the standard render palette: accent for the index
    segment and muted accent for the label segment.

    Args:
        stage (Stage): The stage to render.
        stage_id (int): Zero-based stage index.

    Returns:
        Text: The styled badge renderable.
    """
    label = _format_stage_label(stage) or " "
    badge = Text()
    badge.append("", style=f"{CELL_ACCENT} on {CELL_BACKGROUND}")
    badge.append(f" {stage_id + 1} ", style=f"bold {CELL_TEXT} on {CELL_ACCENT}")
    badge.append(f" {label} ", style=f"bold {CELL_GLOW} on {CELL_BACKGROUND}")
    badge.append("", style=f"{CELL_ACCENT} on {CELL_BACKGROUND}")
    return badge


def _render_horizontal(stages: list[RenderableType], connector: str) -> Table:
    """Render stages side-by-side with connectors between them.

    Args:
        stages (list[RenderableType]): Rendered stages to place horizontally.
        connector (str): Connector text to place between stages.

    Returns:
        Table: The horizontal stage layout.
    """
    panels: list[RenderableType] = []
    for stage_id, stage in enumerate(stages, start=1):
        panels.append(stage)
        if stage_id < len(stages):
            panels.append(Text(f" {connector} ", style=ARROW_STYLE_COLOR))

    table = Table.grid(padding=(0, 0))
    for _ in range(len(panels)):
        table.add_column(vertical="middle", justify="center")
    table.add_row(*panels)
    return table


def _render_vertical(stages: list[RenderableType], connector: str) -> Table:
    """Render stages top-to-bottom with connectors between them.

    Args:
        stages (list[RenderableType]): Rendered stages to place vertically.
        connector (str): Connector text to place between stages.

    Returns:
        Table: The vertical stage layout.
    """
    table = Table.grid(padding=(0, 0))
    table.add_column(justify="left")

    for stage_id, stage in enumerate(stages, start=1):
        table.add_row(stage)
        if stage_id < len(stages):
            table.add_row(Text(f"  {connector}", style=ARROW_STYLE_COLOR))

    return table


def _render_branch_alignment(
    left_stage: RenderableType,
    left_connector: str,
    right_stage_top: RenderableType,
    right_connector: str,
    right_stage_bottom: RenderableType,
) -> Table:
    """Render an OR branch under the preceding AND branch.

    Args:
        left_stage (RenderableType): The left side of the branch.
        left_connector (str): Connector between the left stage and top right stage.
        right_stage_top (RenderableType): The top right branch.
        right_connector (str): Connector between the two right branches.
        right_stage_bottom (RenderableType): The bottom right branch.

    Returns:
        Table: The aligned branch layout.
    """
    blank = Text("")
    table = Table.grid(padding=(0, 1))
    table.add_column(vertical="middle", justify="center")
    table.add_column(vertical="middle", justify="center")
    table.add_column(vertical="middle", justify="center")

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
) -> Table:
    """Render an OR branch below a preceding AND branch.

    Args:
        node (Pipeline): The OR pipeline node to render.
        arrow_style (ArrowStyle): The arrow style configuration.
        stage_counter (Iterator[int]): Counter used to assign stage numbers.

    Returns:
        Table: The aligned branch layout.


    """
    left_stage = _render_node(node.left, arrow_style, stage_counter)
    and_stage = _render_node(node.right, arrow_style, stage_counter)
    or_stage = _render_node(node.right, arrow_style, stage_counter)
    and_connector = node.delimiter.arrow_style(arrow_style)
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
) -> RenderableType:
    """Render one pipeline node as badges connected by arrows.

    Args:
        node (Stage | Pipeline): The node to render.
        arrow_style (ArrowStyle): The arrow style configuration.
        stage_counter (Iterator[int]): Counter used to assign stage numbers.

    Returns:
        RenderableType: The rendered node.
    """
    if isinstance(node, Stage):
        return _render_badge(node, next(stage_counter))

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
    connector = node.delimiter.arrow_style(arrow_style)
    if node.delimiter.is_horizontal():
        return _render_horizontal(rendered_children, connector)

    return _render_vertical(rendered_children, connector)


@logger.catch
def render(
    node: Stage | Pipeline,
    arrow_style: ArrowStyle = "standard",
) -> None:
    """Render a pipeline using numbered Rich badges.

    Args:
        node (Stage | Pipeline): The pipeline structure containing stages to render.
        arrow_style (ArrowStyle): The arrow style configuration for connecting stages.
    """
    rendered_node = _render_node(node, arrow_style, count())
    console.print(rendered_node)
