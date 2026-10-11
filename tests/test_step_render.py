"""Tests for step_render module."""

from pipeline_visualizer.enums import PipelineStatus, StageStatus, TreeConnector
from pipeline_visualizer.parsers import standard_parser
from pipeline_visualizer.renders import step_render
from pipeline_visualizer.renders.step_render import TreeNode

EXPECTED_PIPE_NODES_COUNT = 1
EXPECTED_LOGICAL_NODES_COUNT = 3


def test_ast_to_tree_nodes_pipe():
    """Test _ast_to_tree_nodes with a simple pipe command."""
    ast = standard_parser.parse("cat input.txt | grep search | wc -l")
    nodes = step_render._ast_to_tree_nodes(ast, default_status=StageStatus.SUCCESS)

    assert len(nodes) == EXPECTED_PIPE_NODES_COUNT
    assert isinstance(nodes[0], TreeNode)
    assert nodes[0].label == "Stage 1"
    assert nodes[0].symbol == PipelineStatus.SUCCESS.value
    assert len(nodes[0].children) == EXPECTED_LOGICAL_NODES_COUNT
    assert nodes[0].children[0].label == "cat input.txt"
    assert nodes[0].children[0].symbol == StageStatus.SUCCESS.value


def test_ast_to_tree_nodes_logical_and():
    """Test _ast_to_tree_nodes with logical AND command using PipelineStatus.SUCCESS."""
    ast = standard_parser.parse("mkdir build && cd build && cmake ..")
    nodes = step_render._ast_to_tree_nodes(
        ast, default_pipeline_status=PipelineStatus.SUCCESS
    )

    assert len(nodes) == EXPECTED_LOGICAL_NODES_COUNT
    assert isinstance(nodes[0], TreeNode)
    assert nodes[0].label == "Stage 1"
    assert nodes[0].symbol == PipelineStatus.SUCCESS.value
    assert nodes[0].children[0].label == "mkdir build"


def test_tree_connector_usage():
    """Test that TreeConnector enum values are used in render nodes."""
    ast = standard_parser.parse("a | b")
    nodes = step_render._ast_to_tree_nodes(ast)
    rendered_lines = step_render._render_tree_nodes(nodes)

    assert rendered_lines is not None
    assert TreeConnector.BRANCH.value == "├─"
    assert TreeConnector.LAST_BRANCH.value == "└─"
    assert TreeConnector.CONNECTORS.value == "│"


def test_step_render_render_call():
    """Test calling step_render.render function directly."""
    ast = standard_parser.parse("echo test")
    # Should run without throwing exceptions
    step_render.render(
        ast, status=StageStatus.SUCCESS, pipeline_status=PipelineStatus.SUCCESS
    )
