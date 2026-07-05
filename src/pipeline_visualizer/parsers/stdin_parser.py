"""Parse command-line pipeline strings into structured pipeline objects.

This module provides utilities for detecting top-level delimiters in shell
pipeline commands, splitting pipelines into stages, parsing conditional
operators, and constructing a normalized pipeline representation.
"""

from lark import Lark
from loguru import logger

from pipeline_visualizer.models import Pipeline
from pipeline_visualizer.transformer import PipelineTransformer


class StandardParser:
    """Parser for standard shell pipelines.

    This parser uses a Lark grammar to parse shell pipeline commands into a
    structured representation. It supports logical operators, pipes, and
    redirection.
    """

    def __init__(self):
        self.grammar = r"""
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

            ?atom: command
                | "(" or_expr ")"

            command: COMMAND+

            COMMAND: /[^|&<>()\s]+/

            %ignore /\s+/
        """
        self._parser = Lark(
            self.grammar,
            start="start",
            parser="lalr",
            transformer=PipelineTransformer(),
        )

    @logger.catch
    def parse(self, pipeline_cmd: str) -> Pipeline:
        """Parse stdin commands.

        Args:
            pipeline_cmd (str): Bash pipeline to parse commands.

        Returns:
            Pipeline: Pipeline representation.
        """
        return self._parser.parse(pipeline_cmd.strip())  # type: ignore[return-value]  # ty:ignore[invalid-return-type]


parser = StandardParser()
