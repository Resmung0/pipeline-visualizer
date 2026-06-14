"""Command-line entry point for the pipeline-visualizer tool.

Provides a CLI command to render pipeline stages parsed from
stdin input. Exposes the `pipeline` command which accepts a pipeline
definition and an optional arrow style.
"""

from typing import Annotated, Literal

import typer

from pipeline_visualizer.enums import HelperText
from pipeline_visualizer.parsers import stdin_parser
from pipeline_visualizer.renders import standard_render

app = typer.Typer()


@app.command()
def pipeline(
    cmd: Annotated[str, typer.Argument(help=HelperText.PIPELINE)],
    arrow: Annotated[
        Literal["standard", "alternative", "thick", "triangle"] | None,
        typer.Option(help=HelperText.ARROW),
    ] = None,
):
    """Render a pipeline diagram from a command string.

    Args:
        cmd: The pipeline definition string to parse from stdin.
        arrow: Optional arrow style to use for rendering. If None,
            the "standard" style is used.
    """
    stages = stdin_parser.parse(cmd)
    standard_render.render(stages, arrow=arrow or "standard")


if __name__ == "__main__":
    app()
