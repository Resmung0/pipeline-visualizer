"""Render pipeline stages using a tree structure with Rich panel."""

from __future__ import annotations

from loguru import logger
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from pipeline_visualizer.enums import (
    Operator,
    PipelineStatus,
    Redirect,
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


def _status_style(status: StageStatus) -> str:
    """Return the style associated with a stage status.

    Args:
        status (StageStatus): The status of the stage.

    Returns:
        str: Style name for Rich text formatting.
    """
    match status:
        case StageStatus.SUCCESS:
            return "green"
        case StageStatus.ERROR:
            return "red"
        case StageStatus.WARNING:
            return "yellow"
        case StageStatus.SKIPPED:
            return "dim"
        case StageStatus.RUNNING:
            return "cyan"
        case StageStatus.PENDING:
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


def _ast_to_nodes(
    node: Stage | Pipeline,
    preceding_op: Operator | None = None,
    status: StageStatus = StageStatus.SUCCESS,
) -> list[dict]:
    """Convert pipeline AST into a node tree structure.

    Args:
        node (Stage | Pipeline): Pipeline AST node.
        preceding_op (Operator | None): Preceding operator for this node.
        status (StageStatus): Default status for the stages.

    Returns:
        list[dict]: List of formatted tree nodes.
    """
    if isinstance(node, Stage):
        label = _format_stage(node)
        detail = f"operator: {preceding_op.value}" if preceding_op else None
        return [{"label": label, "status": status, "detail": detail, "children": []}]

    delim = node.delimiter

    if isinstance(delim, Redirect):
        target_file = (
            _format_stage(node.right) if isinstance(node.right, Stage) else "target"
        )
        nodes = _ast_to_nodes(node.left, preceding_op, status)
        if nodes:
            redirect_info = f"redirect {delim.value} {target_file}"
            nodes[0]["detail"] = (
                f"{nodes[0]['detail']} | {redirect_info}"
                if nodes[0]["detail"]
                else redirect_info
            )
        return nodes

    if delim == Operator.PIPE:
        pipe_stages = _flatten_pipe(node)
        res: list[dict] = []
        for idx, stage in enumerate(pipe_stages):
            op = None if idx == 0 else Operator.PIPE
            res.extend(_ast_to_nodes(stage, op, status))
        return res

    if delim in (Operator.AND, Operator.OR, Operator.SEMICOLON):
        logical_items = _flatten_logical(node)
        res = []
        for item, op in logical_items:
            res.extend(_ast_to_nodes(item, op, status))
        return res

    return [{"label": str(node), "status": status, "detail": None, "children": []}]


def _render_tree_node(
    node_dict: dict,
    prefix: str,
    connector: str | None,
    is_last: bool,
) -> list[Text]:
    """Render a single node and its children into Rich Text objects.

    Args:
        node_dict (dict): Node dictionary.
        prefix (str): Indentation prefix.
        connector (str | None): Tree branch connector.
        is_last (bool): True if last node among siblings.

    Returns:
        list[Text]: Formatted lines of Rich text.
    """
    lines: list[Text] = []
    line = Text()

    if connector:
        line.append(prefix + connector + " ", style="dim")
    else:
        line.append(prefix)

    status: StageStatus = node_dict.get("status", StageStatus.SUCCESS)
    line.append(status.value, style=_status_style(status))
    line.append(f" {node_dict['label']}")
    lines.append(line)

    detail = node_dict.get("detail")
    children: list[dict] = node_dict.get("children", [])

    if detail:
        detail_prefix = prefix + (
            "   " if is_last else f"{TreeConnector.connectors.value}  "
        )
        lines.append(
            Text(
                f"{detail_prefix}{TreeConnector.last_branch.value} {detail}",
                style="dim",
            )
        )

    for index, child in enumerate(children):
        child_is_last = index == len(children) - 1
        child_connector = (
            TreeConnector.last_branch.value
            if child_is_last
            else TreeConnector.branch.value
        )
        child_prefix = prefix + (
            "   " if is_last else f"{TreeConnector.connectors.value}  "
        )
        lines.extend(
            _render_tree_node(child, child_prefix, child_connector, child_is_last)
        )

    return lines


def _render_nodes(nodes: list[dict]) -> Group:
    """Render a list of top-level nodes into a Rich Group.

    Args:
        nodes (list[dict]): List of node dictionaries.

    Returns:
        Group: Group of formatted Rich Text lines.
    """
    lines: list[Text] = []
    for index, node in enumerate(nodes):
        is_last = index == len(nodes) - 1
        connector = (
            TreeConnector.last_branch.value if is_last else TreeConnector.branch.value
        )
        lines.extend(_render_tree_node(node, "", connector, is_last))
    return Group(*lines)


@logger.catch
def render(
    pipeline: Stage | Pipeline,
    title: str = "Pipeline",
    status: StageStatus = StageStatus.SUCCESS,
    pipeline_status: PipelineStatus = PipelineStatus.SUCCESS,
    border_style: str = "dim",
) -> None:
    """Render a pipeline structure using tree connectors and stage status symbols.

    Args:
        pipeline (Stage | Pipeline): The parsed pipeline AST to render.
        title (str): Panel title for the pipeline visualization. Defaults to "Pipeline".
        status (StageStatus): Default status for pipeline stages. Defaults to StageStatus.SUCCESS.
        pipeline_status (PipelineStatus): Overall pipeline status indicator. Defaults to PipelineStatus.SUCCESS.
        border_style (str): Border style for the Rich panel. Defaults to "dim".
    """
    nodes = _ast_to_nodes(pipeline, status=status)
    content = _render_nodes(nodes)
    panel_title = f"{pipeline_status.value} {title}" if pipeline_status else title
    panel = Panel(content, title=panel_title, border_style=border_style, padding=(1, 2))
    console.print(panel)
