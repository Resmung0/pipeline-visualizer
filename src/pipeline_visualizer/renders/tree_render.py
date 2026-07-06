"""Render pipeline stages using a tree structure."""

from loguru import logger
from rich.console import Console
from rich.tree import Tree

from pipeline_visualizer.enums import Operator, Redirect
from pipeline_visualizer.models import Pipeline, Stage

console = Console()


def _stage_icon(operator: Operator | None) -> str:
    """Return the icon that represents a logical stage operator.

    Args:
        operator (Operator | None): The logical operator for the stage.

    Returns:
        str: The icon representing the stage operator.
    """
    if operator == Operator.OR:
        return "🔀"
    if operator == Operator.SEMICOLON:
        return "⌛"

    return "✅"


def _format_node(node: Stage | Pipeline) -> str:
    """Format a node (Stage or Pipeline) into a string representation.

    Args:
        node (Stage | Pipeline): The node to format.

    Returns:
        str: String representation of the node.
    """
    if isinstance(node, Stage):
        return " ".join(
            part
            for part in (node.command, node.subcommand, node.parameter)
            if part is not None
        )

    left = _format_node(node.left)
    right = _format_node(node.right)

    if node.delimiter == Operator.PIPE:
        return f"{left} ── {right}"
    if isinstance(node.delimiter, Redirect):
        return f"{left} {node.delimiter.value} {right}"

    return f"{left} {node.delimiter.value} {right}"


def _flatten_logical_structure(
    node: Stage | Pipeline,
) -> list[tuple[Stage | Pipeline, Operator | None]]:
    """Flatten the pipeline into logical stages based on AND, OR, and SEMICOLON.

    Args:
        node (Stage | Pipeline): The root node of the pipeline.

    Returns:
        list[tuple[Stage | Pipeline, Operator | None]]: A list of nodes and their preceding operators.
    """
    if isinstance(node, Stage):
        return [(node, None)]

    if isinstance(node, Pipeline) and node.delimiter in {
        Operator.AND,
        Operator.OR,
        Operator.SEMICOLON,
    }:
        left_flattened = _flatten_logical_structure(node.left)
        right_flattened = _flatten_logical_structure(node.right)

        # Update the first element of the right flattened list with the current delimiter
        first_right_node, _ = right_flattened[0]
        # Cast node.delimiter to Operator since we checked it's one of the Operator members above
        op = node.delimiter
        if isinstance(op, Operator):
            updated_right_head = (first_right_node, op)
            return left_flattened + [updated_right_head] + right_flattened[1:]

    return [(node, None)]


def _render_logical_tree(
    flattened: list[tuple[Stage | Pipeline, Operator | None]],
) -> str:
    """Render logical branches aligned with the end of the base expression.

    Args:
        flattened (list[tuple[Stage | Pipeline, Operator | None]]): A list of nodes and their preceding operators.

    Returns:
        str: A string representation of the logical tree.
    """
    first_node, _ = flattened[0]
    base_expression = _format_node(first_node)
    base_prefix = "    └── "
    branch_indent = " " * (len(base_prefix) + len(base_expression))

    lines = [
        "• Pipeline",
        "└── 📦 Stage 1",
        f" {base_prefix}{base_expression}",
    ]

    follow_up_stages = flattened[1:]
    for index, (node, operator) in enumerate(follow_up_stages, start=2):
        is_last = index == len(flattened)
        branch = "└──" if is_last else "├──"
        child_guide = "     " if is_last else "│    "
        icon = _stage_icon(operator)

        lines.append(f"{branch_indent}{branch} {icon} Stage {index}")
        lines.append(f"{branch_indent}{child_guide}└── {_format_node(node)}")

    return "\n".join(lines)


@logger.catch
def render(pipeline: Stage | Pipeline) -> None:
    """Render the pipeline in a tree format.

    Args:
        pipeline (Stage | Pipeline): The pipeline structure to render.
    """
    tree = Tree("• Pipeline")
    flattened = _flatten_logical_structure(pipeline)

    if not flattened:
        return

    if len(flattened) > 1:
        console.print(_render_logical_tree(flattened), markup=False, highlight=False)
        return

    # First stage is the root of the tree visualization
    first_node, _ = flattened[0]
    stage_node = tree.add("📦 Stage 1")
    stage_node.add(_format_node(first_node))

    console.print(tree)
