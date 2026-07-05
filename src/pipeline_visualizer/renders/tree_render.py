"""Render pipeline stages using a tree structure."""

from rich.console import Console
from rich.tree import Tree

from pipeline_visualizer.enums import Operator, Redirect
from pipeline_visualizer.models import Pipeline, Stage

console = Console()


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

    if (
        isinstance(node, Pipeline)
        and node.delimiter in {Operator.AND, Operator.OR, Operator.SEMICOLON}
    ):
        left_flattened = _flatten_logical_structure(node.left)
        right_flattened = _flatten_logical_structure(node.right)

        # Update the first element of the right flattened list with the current delimiter
        first_right_node, _ = right_flattened[0]
        # Cast node.delimiter to Operator since we checked it's one of the Operator members above
        op = node.delimiter
        if isinstance(op, Operator):
            updated_right_head: tuple[Stage | Pipeline, Operator | None] = (
                first_right_node,
                op,
            )
            return left_flattened + [updated_right_head] + right_flattened[1:]

    return [(node, None)]


def render(pipeline: Stage | Pipeline) -> None:
    """Render the pipeline in a tree format.

    Args:
        pipeline (Stage | Pipeline): The pipeline structure to render.
    """
    tree = Tree(" • Pipeline")
    flattened = _flatten_logical_structure(pipeline)

    if not flattened:
        return

    # First stage is the root of the tree visualization
    first_node, _ = flattened[0]
    stage_node = tree.add("📦 Stage 1")
    content_node = stage_node.add(_format_node(first_node))

    if len(flattened) > 1:
        # Subsequent stages are grouped under a "|" connector attached to the first stage's content
        connector = content_node.add("|")
        for i, (node, operator) in enumerate(flattened[1:], start=2):
            icon = "✅"
            operator_label = "&&"
            if operator == Operator.OR:
                icon = "🔀"
                operator_label = "||"
            elif operator == Operator.SEMICOLON:
                icon = "⌛"
                operator_label = ";"

            st = connector.add(f"{icon} Stage {i} ({operator_label})")
            st.add(_format_node(node))

    console.print(tree)
