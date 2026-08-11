"""Render pipeline stages using a tree structure with Rich panel."""

from __future__ import annotations

from loguru import logger
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from pipeline_visualizer.enums import (
    Operator,
    PipelineStatus,
    StageStatus,
    TreeConnector,
)
from pipeline_visualizer.models import Pipeline, Stage

console = Console(color_system="truecolor")


def _format_stage(stage: Stage) -> str:
    """Format a stage into a space-joined command string.

    Args:
        stage (Stage): Stage model object.

    Returns:
        str: Formatted command string.
    """
    return " ".join(
        part for part in (stage.command, stage.subcommand, stage.parameter) if part
    )


def _format_node(node: Stage | Pipeline) -> str:
    """Format an AST node into a string representation.

    Args:
        node (Stage | Pipeline): The AST node to format.

    Returns:
        str: String representation of the node.
    """
    if isinstance(node, Stage):
        return _format_stage(node)

    left = _format_node(node.left)
    right = _format_node(node.right)
    return f"{left} {node.delimiter.value} {right}"


def _status_style(status: StageStatus | PipelineStatus) -> str:
    """Return the style associated with a status indicator.

    Args:
        status (StageStatus | PipelineStatus): Status value.

    Returns:
        str: Style string for Rich text.
    """
    match status:
        case StageStatus.SUCCESS | PipelineStatus.SUCCESS:
            return "green"
        case StageStatus.ERROR | PipelineStatus.ERROR:
            return "red"
        case StageStatus.WARNING | PipelineStatus.WARNING:
            return "yellow"
        case StageStatus.SKIPPED | PipelineStatus.SKIPPED:
            return "dim"
        case StageStatus.RUNNING | PipelineStatus.RUNNING:
            return "cyan"
        case StageStatus.PENDING | PipelineStatus.PENDING:
            return "dim"


def _flatten_logical(
    node: Stage | Pipeline,
) -> list[tuple[Stage | Pipeline, Operator | None]]:
    """Flatten logical operators (AND, OR, SEMICOLON) into a sequence.

    Args:
        node (Stage | Pipeline): Pipeline AST node.

    Returns:
        list[tuple[Stage | Pipeline, Operator | None]]: Sequence of nodes with preceding operators.
    """
    if isinstance(node, Stage):
        return [(node, None)]
    if isinstance(node, Pipeline) and node.delimiter in (
        Operator.AND,
        Operator.OR,
        Operator.SEMICOLON,
    ):
        left_flat = _flatten_logical(node.left)
        right_flat = _flatten_logical(node.right)
        op = node.delimiter
        first_right, _ = right_flat[0]
        if isinstance(op, Operator):
            return left_flat + [(first_right, op)] + right_flat[1:]
    return [(node, None)]


def _flatten_pipe(node: Stage | Pipeline) -> list[Stage | Pipeline]:
    """Flatten chained pipe operators into a list of nodes.

    Args:
        node (Stage | Pipeline): Pipeline AST node.

    Returns:
        list[Stage | Pipeline]: List of piped nodes.
    """
    if isinstance(node, Stage):
        return [node]
    if isinstance(node, Pipeline) and node.delimiter == Operator.PIPE:
        return _flatten_pipe(node.left) + _flatten_pipe(node.right)
    return [node]


def _ast_to_tree_nodes(
    node: Stage | Pipeline,
    default_status: StageStatus = StageStatus.SUCCESS,
    default_pipeline_status: PipelineStatus = PipelineStatus.SUCCESS,
) -> list[dict]:
    """Convert pipeline AST into numbered Stage tree nodes for rendering.

    Displays 'Stage 1', 'Stage 2', etc. next to PipelineStatus.SUCCESS ('◆'),
    and places command details below in dark gray with StageStatus.SUCCESS ('●').

    Args:
        node (Stage | Pipeline): Pipeline AST node.
        default_status (StageStatus): Default status for stage items.
        default_pipeline_status (PipelineStatus): Default status for pipeline items.

    Returns:
        list[dict]: Hierarchy of tree nodes for rendering.
    """
    if isinstance(node, Pipeline) and node.delimiter in (
        Operator.AND,
        Operator.OR,
        Operator.SEMICOLON,
    ):
        logical_items = _flatten_logical(node)
        tree_nodes: list[dict] = []
        for idx, (item, op) in enumerate(logical_items, start=1):
            item_status = (
                PipelineStatus.ERROR if op == Operator.OR else default_pipeline_status
            )
            stage_title = f"Stage {idx}"

            if isinstance(item, Stage):
                children = [
                    {
                        "symbol": default_status.value,
                        "status": default_status,
                        "label": _format_stage(item),
                        "is_command": True,
                        "children": [],
                    }
                ]
            elif isinstance(item, Pipeline) and item.delimiter == Operator.PIPE:
                pipe_stages = _flatten_pipe(item)
                children = [
                    {
                        "symbol": default_status.value,
                        "status": default_status,
                        "label": _format_stage(s),
                        "is_command": True,
                        "children": [],
                    }
                    for s in pipe_stages
                ]
            else:
                children = [
                    {
                        "symbol": default_status.value,
                        "status": default_status,
                        "label": _format_node(item),
                        "is_command": True,
                        "children": [],
                    }
                ]

            tree_nodes.append(
                {
                    "symbol": item_status.value,
                    "status": item_status,
                    "label": stage_title,
                    "is_command": False,
                    "children": children,
                }
            )
        return tree_nodes

    if isinstance(node, Pipeline) and node.delimiter == Operator.PIPE:
        pipe_stages = _flatten_pipe(node)
        children = [
            {
                "symbol": default_status.value,
                "status": default_status,
                "label": _format_stage(s),
                "is_command": True,
                "children": [],
            }
            for s in pipe_stages
        ]
        return [
            {
                "symbol": default_pipeline_status.value,
                "status": default_pipeline_status,
                "label": "Stage 1",
                "is_command": False,
                "children": children,
            }
        ]

    return [
        {
            "symbol": default_pipeline_status.value,
            "status": default_pipeline_status,
            "label": "Stage 1",
            "is_command": False,
            "children": [
                {
                    "symbol": default_status.value,
                    "status": default_status,
                    "label": _format_node(node),
                    "is_command": True,
                    "children": [],
                }
            ],
        }
    ]


def _render_tree_nodes(
    nodes: list[dict],
    prefix: str = "",
) -> list[Text]:
    """Render tree nodes into lines of Rich Text.

    Args:
        nodes (list[dict]): Tree nodes to render.
        prefix (str): Indentation prefix string.

    Returns:
        list[Text]: Formatted lines of Rich text.
    """
    lines: list[Text] = []
    for index, n in enumerate(nodes):
        is_last = index == len(nodes) - 1
        connector = (
            TreeConnector.last_branch.value if is_last else TreeConnector.branch.value
        )

        line = Text()
        if prefix or connector:
            line.append(prefix + connector + " ", style="dim")

        status_val = n.get("status", StageStatus.SUCCESS)
        line.append(n["symbol"], style=_status_style(status_val))

        label_style = "dim" if n.get("is_command") else "bold white"
        line.append(f" {n['label']}", style=label_style)
        lines.append(line)

        if n["children"]:
            child_prefix = prefix + (
                "   " if is_last else f"{TreeConnector.connectors.value}  "
            )
            lines.extend(_render_tree_nodes(n["children"], child_prefix))

    return lines


@logger.catch
def render(
    pipeline: Stage | Pipeline,
    title: str = "Pipeline",
    status: StageStatus = StageStatus.SUCCESS,
    pipeline_status: PipelineStatus = PipelineStatus.SUCCESS,
    border_style: str = "dim",
) -> None:
    """Render a pipeline structure using tree connectors and stage/pipeline status symbols.

    Args:
        pipeline (Stage | Pipeline): The parsed pipeline AST to render.
        title (str): Panel title for the pipeline visualization. Defaults to "Pipeline".
        status (StageStatus): Default status for commands in pipe. Defaults to StageStatus.SUCCESS.
        pipeline_status (PipelineStatus): Default status for pipeline Stage nodes. Defaults to PipelineStatus.SUCCESS.
        border_style (str): Border style for the Rich panel. Defaults to "dim".
    """
    nodes = _ast_to_tree_nodes(
        pipeline, default_status=status, default_pipeline_status=pipeline_status
    )
    lines = _render_tree_nodes(nodes)
    content = Group(*lines)
    panel_title = f"{pipeline_status.value} {title}" if pipeline_status else title
    panel = Panel(content, title=panel_title, border_style=border_style, padding=(1, 2))
    console.print(panel)
