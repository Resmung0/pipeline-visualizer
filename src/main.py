"""Command-line entry point for the pipeline-visualizer tool.

Provides a CLI command to render pipeline stages parsed from
stdin input. Exposes the `pipeline` command which accepts a pipeline
definition and an optional arrow style.
"""

from cyclopts import App

from pipeline_visualizer.parsers import stdin_parser
from pipeline_visualizer.renders import standard_render
from pipeline_visualizer.types import ArrowStyle

app = App()


@app.default
def pipeline(cmd: str, arrow: ArrowStyle | None = None) -> None:
    """Render a pipeline diagram from a command string.

    Args:
        cmd (str): The shell pipeline command to visualize.
        arrow (ArrowStyle | None): Arrow style of the visualization. Defaults to None.
    """
    stages = stdin_parser.parse(cmd)
    standard_render.render(stages, arrow_style=arrow or "standard")


if __name__ == "__main__":
    app()
