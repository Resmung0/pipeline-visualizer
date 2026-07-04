"""Parse command-line pipeline strings into structured pipeline objects.

This module provides utilities for detecting top-level delimiters in shell
pipeline commands, splitting pipelines into stages, parsing conditional
operators, and constructing a normalized pipeline representation.
"""

from lark import Lark
from loguru import logger

from pipeline_visualizer.models import Pipeline
from pipeline_visualizer.transformer import PipelineTransformer


@logger.catch
def parse(pipeline_cmd: str) -> Pipeline:
    """Parse stdin commands.

    Args:
        pipeline_cmd (str): Bash pipeline to parse commands.

    Returns:
        Pipeline: Pipeline representation.
    """
    grammar = r"""
    ?start: or_expr

    ?or_expr: and_expr
            | or_expr "||" and_expr   -> logical_or

    ?and_expr: semicolon_expr
            | and_expr "&&" semicolon_expr -> logical_and

    ?semicolon_expr: pipe_expr
            | semicolon_expr ";" pipe_expr -> semmicolon

    ?pipe_expr: redirect_expr
            | pipe_expr "|" redirect_expr -> pipe

    ?redirect_expr: atom
                | redirect_expr ">" atom   -> redirect_out
                | redirect_expr ">>" atom  -> redirect_out_append
                | redirect_expr "<" atom   -> redirect_in
                | redirect_expr "<<" atom   -> redirect_in_append

    ?atom: COMMAND
        | "(" or_expr ")"

    COMMAND: /[^|&<>()\s]+/

    %ignore /\s+/
    """

    # Cria o parser
    parser = Lark(
        grammar, start="start", parser="lalr", transformer=PipelineTransformer()
    )
    return parser.parse(pipeline_cmd.strip())  # type: ignore[return-value]  # ty:ignore[invalid-return-type]
