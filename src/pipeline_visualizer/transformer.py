"""Transform parse trees into pipeline AST nodes."""

from typing import Any

from lark import Transformer, v_args

from pipeline_visualizer.enums import Operator, Redirect
from pipeline_visualizer.models import Pipeline, Stage


@v_args(inline=True)
class PipelineTransformer(Transformer):
    """Transform parse trees into pipeline AST nodes."""

    def COMMAND(self, token: Any) -> Stage:  # noqa: N802
        """Convert a COMMAND token into a Stage node.

        Args:
            token (Any): The COMMAND token from the parse tree.

        Returns:
            Stage: A new Stage node representing the command.
        """
        return Stage(str(token))

    def pipe(self, left: Stage | Pipeline, right: Stage | Pipeline) -> Pipeline:
        """Create a pipeline node for the pipe operator.

        Args:
            left (Stage | Pipeline): The left stage or pipeline.
            right (Stage | Pipeline): The right stage or pipeline.

        Returns:
            Pipeline: A new Pipeline node representing the pipe operation.
        """
        return Pipeline(Operator.PIPE, left, right)

    def logical_and(self, left: Stage | Pipeline, right: Stage | Pipeline) -> Pipeline:
        """Create a pipeline node for logical AND.

        Args:
            left (Stage | Pipeline): The left stage or pipeline.
            right (Stage | Pipeline): The right stage or pipeline.

        Returns:
            Pipeline: A new Pipeline node representing the logical AND operation.
        """
        return Pipeline(Operator.AND, left, right)

    def logical_or(self, left: Stage | Pipeline, right: Stage | Pipeline) -> Pipeline:
        """Create a pipeline node for logical OR.

        Args:
            left (Stage | Pipeline): The left stage or pipeline.
            right (Stage | Pipeline): The right stage or pipeline.

        Returns:
            Pipeline: A new Pipeline node representing the logical OR operation.
        """
        return Pipeline(Operator.OR, left, right)

    def semmicolon(self, left: Stage | Pipeline, right: Stage | Pipeline) -> Pipeline:
        """Create a pipeline node for a semicolon separator.

        Args:
            left (Stage | Pipeline): The left stage or pipeline.
            right (Stage | Pipeline): The right stage or pipeline.

        Returns:
            Pipeline: A new Pipeline node representing the semicolon separator.
        """
        return Pipeline(Operator.SEMICOLON, left, right)

    def redirect_out(self, left: Stage | Pipeline, right: Stage | Pipeline) -> Pipeline:
        """Create a pipeline node for output redirection.

        Args:
            left (Stage | Pipeline): The left stage or pipeline.
            right (Stage | Pipeline): The right stage or pipeline.

        Returns:
            Pipeline: A new Pipeline node representing the output redirection.
        """
        return Pipeline(Redirect.OUT, left, right)

    def redirect_out_append(
        self, left: Stage | Pipeline, right: Stage | Pipeline
    ) -> Pipeline:
        """Create a pipeline node for appended output redirection.

        Args:
            left (Stage | Pipeline): The left stage or pipeline.
            right (Stage | Pipeline): The right stage or pipeline.

        Returns:
            Pipeline: A new Pipeline node representing the appended output redirection.
        """
        return Pipeline(Redirect.OUT_APPEND, left, right)

    def redirect_in(self, left: Stage | Pipeline, right: Stage | Pipeline) -> Pipeline:
        """Create a pipeline node for input redirection.

        Args:
            left (Stage | Pipeline): The left stage or pipeline.
            right (Stage | Pipeline): The right stage or pipeline.

        Returns:
            Pipeline: A new Pipeline node representing the input redirection.
        """
        return Pipeline(Redirect.IN, left, right)

    def redirect_in_append(
        self, left: Stage | Pipeline, right: Stage | Pipeline
    ) -> Pipeline:
        """Create a pipeline node for appended input redirection.

        Args:
            left (Stage | Pipeline): The left stage or pipeline.
            right (Stage | Pipeline): The right stage or pipeline.

        Returns:
            Pipeline: A new Pipeline node representing the appended input redirection.
        """
        return Pipeline(Redirect.IN_APPEND, left, right)
