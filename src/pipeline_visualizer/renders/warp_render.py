"""Render pipeline stages with Warp-inspired terminal cells."""

import shlex
from collections.abc import Iterator
from itertools import count

from loguru import logger
from rich.console import Console, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pipeline_visualizer.constants import ARROW_STYLE_COLOR
from pipeline_visualizer.enums import Operator
from pipeline_visualizer.models import Pipeline, Stage
from pipeline_visualizer.types import ArrowStyle

console = Console(color_system="truecolor")

CELL_BACKGROUND = "#351935"
CELL_GLOW = "#ff196f"
CELL_ACCENT = "#ff196f"
CELL_ACCENT_MUTED = "#ff77ad"
CELL_TEXT = "#f8f4ff"
CELL_DIM = "#a9a0b4"


def _format_command(stage: Stage) -> str:
    """Return a shell-like command string for a stage.

    Args:
        stage (Stage): The stage to format.

    Returns:
        str: The command string for the stage.
    """
    return " ".join(
        part for part in (stage.command, stage.subcommand, stage.parameter) if part
    )


def _command_text(command: str) -> Text:
    """Style the executable and arguments as a terminal prompt line.

    Args:
        command (str): The command string to style.

    Returns:
        Text: The styled command line.
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    if not tokens:
        return Text("", style=f"bold {CELL_TEXT}")

    executable, *args = tokens
    text = Text("", style=f"bold {CELL_TEXT}")
    text.append(executable, style=f"bold {CELL_ACCENT_MUTED}")
    if args:
        text.append(" ")
        text.append(" ".join(args), style=f"bold {CELL_TEXT}")
    return text


def _cell_body(stage: Stage) -> Table:
    """Build the content area inside a Warp-like cell.

    Args:
        stage (Stage): The stage to render.

    Returns:
        Table: The renderable cell body.
    """
    body = Table.grid(expand=True, padding=(0, 0))
    body.add_column(ratio=1, style=f"on {CELL_BACKGROUND}", no_wrap=False)
    body.add_row(_command_text(_format_command(stage)))
    return body


def _render_stage(stage: Stage, stage_id: int) -> Panel:
    """Render one stage with an accent rail and matching background glow.

    Args:
        stage (Stage): The stage to render.
        stage_id (int): The zero-based stage index.

    Returns:
        Panel: The Warp-inspired stage cell.
    """
    table = Table.grid(expand=True, padding=(0, 0))
    table.add_column(width=1, style=f"on {CELL_ACCENT}")
    table.add_column(width=1, style=f"on {CELL_BACKGROUND}")

    table.add_row(
        Text(" ", style=f"on {CELL_ACCENT}"),
        Text("  ", style=f"on {CELL_BACKGROUND}"),
        Padding(_cell_body(stage), (0, 2), style=f"on {CELL_BACKGROUND}"),
    )

    return Panel(
        table,
        border_style=CELL_GLOW,
        padding=(0, 0),
        style=f"on {CELL_BACKGROUND}",
        expand=False,
        title=Text(f"Stage {stage_id + 1}", style=f"bold {CELL_DIM}"),
    )


def _render_horizontal(stages: list[RenderableType], connector: str) -> Table:
    """Render stages side-by-side.

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
            panels.append(Text(connector, style=ARROW_STYLE_COLOR))

    table = Table.grid(padding=(0, 1))
    for panel_id in range(len(panels)):
        table.add_column(
            vertical="middle" if panel_id % 2 == 1 else "top",
            justify="center",
        )
    table.add_row(*panels)
    return table


def _render_vertical(stages: list[RenderableType], connector: str) -> Table:
    """Render stages top-to-bottom.

    Args:
        stages (list[RenderableType]): Rendered stages to place vertically.
        connector (str): Connector text to place between stages.

    Returns:
        Table: The vertical stage layout.
    """
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
    table.add_column(vertical="top", justify="center")
    table.add_column(vertical="middle", justify="center")
    table.add_column(vertical="top", justify="center")

    table.add_row(
        left_stage,
        Text(left_connector, style=ARROW_STYLE_COLOR),
        right_stage_top,
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
        stage_counter (Iterator[int]): Counter used to assign stage numbers

    Returns:
        Table: The aligned branch layout.

    Raises:
        TypeError: If the left side of the OR node is not an AND pipeline.
    """
    left = node.left
    if not isinstance(left, Pipeline):
        raise TypeError("OR branch alignment requires a pipeline on the left side.")

    left_stage = _render_node(left.left, arrow_style, stage_counter)
    and_stage = _render_node(left.right, arrow_style, stage_counter)
    or_stage = _render_node(node.right, arrow_style, stage_counter)
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
) -> RenderableType:
    """Render one pipeline node using the existing panel layout semantics.

    Args:
        node (Stage | Pipeline): The node to render.
        arrow_style (ArrowStyle): The arrow style configuration.
        stage_counter (Iterator[int]): Counter used to assign stage numbers.

    Returns:
        RenderableType: The rendered node.
    """
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
    connector = node.delimiter.arrow_style(arrow_style)
    if node.delimiter.is_horizontal():
        return _render_horizontal(rendered_children, connector)

    return _render_vertical(rendered_children, connector)


@logger.catch
def render(node: Stage | Pipeline, arrow_style: ArrowStyle = "standard") -> None:
    """Render a pipeline as Warp-inspired terminal cells.

    Args:
        node (Stage | Pipeline): The pipeline structure containing stages to render.
        arrow_style (ArrowStyle): The arrow style configuration for connectors.
    """
    console.print(_render_node(node, arrow_style, count()))
