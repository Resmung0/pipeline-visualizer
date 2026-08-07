"""Command-line entry point for the pipeline-visualizer tool.

Provides a CLI command to render pipeline stages parsed from
stdin input. Exposes the `pipeline` command which accepts a pipeline
definition and an optional arrow style.
"""

from typing import Literal

from cyclopts import App, Parameter

from pipeline_visualizer.parsers import standard_parser
from pipeline_visualizer.renders import standard_render, tree_render
from pipeline_visualizer.types import ArrowStyle, PipelineCommand, TitlePosition

app = App(default_parameter=Parameter(short_alias=True))


@app.default
def pipeline(
    cmd: PipelineCommand,
    /,
    *,
    arrow: ArrowStyle | None = None,
    layout: Literal["panel", "tree"] = "panel",
    title_position: TitlePosition = "top",
) -> None:
    """Render a pipeline diagram from a command string.

    Args:
        cmd (PipelineCommand): The shell pipeline command to visualize.
        arrow (ArrowStyle | None): Arrow style of the visualization. Defaults to None.
        layout (Literal["panel", "tree"]): Layout style of the visualization. Defaults to "panel".
        title_position (TitlePosition): Position of the stage name/title in the panels. Defaults to "top".
    """
    parsed_pipeline = standard_parser.parse(cmd)

    match layout:
        case "panel":
            standard_render.render(
                parsed_pipeline,
                arrow_style=arrow or "standard",
                title_position=title_position,
            )
        case "tree":
            tree_render.render(parsed_pipeline)


if __name__ == "__main__":
    app()
