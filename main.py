from typing import Annotated

import typer

from src.pipeline_visualizer.enums import Arrows, HelperText
from src.pipeline_visualizer.parsers import stdin_parser
from src.pipeline_visualizer.renders import standard_render

app = typer.Typer()


@app.command()
def main(
    pipeline: Annotated[str, typer.Argument(help=HelperText.PIPELINE)],
    arrow: Annotated[Arrows, typer.Option(help=HelperText.ARROW)] = Arrows.THICK,
):
    stages = stdin_parser.parse(pipeline)
    standard_render.render(stages, arrows=arrow)


if __name__ == "__main__":
    app()
