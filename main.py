from typing import Annotated

import typer

from src.pipeline_visualizer.enums import HelperText
from src.pipeline_visualizer.parsers import stdin_parser
from src.pipeline_visualizer.renders import standard_render

app = typer.Typer()


@app.command()
def main(
    pipeline: Annotated[str, typer.Argument(help=HelperText.PIPELINE)],
):
    stages = stdin_parser.parse(pipeline)
    standard_render.render(stages)


if __name__ == "__main__":
    app()
