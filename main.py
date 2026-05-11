from typing import Annotated, Literal

import typer

# from loguru import logger
from src.pipeline_visualizer.enums import HelperText
from src.pipeline_visualizer.parsers import stdin_parser
from src.pipeline_visualizer.renders import standard_render

# logger.disable("my_library")
app = typer.Typer()


@app.command()
def pipeline(
    cmd: Annotated[str, typer.Argument(help=HelperText.PIPELINE)],
    arrow: Annotated[
        Literal["standard", "alternative", "thick", "triangle"] | None,
        typer.Option(help=HelperText.ARROW),
    ] = None,
):
    stages = stdin_parser.parse(cmd)
    standard_render.render(stages, arrows=arrow or "standard")


if __name__ == "__main__":
    app()
