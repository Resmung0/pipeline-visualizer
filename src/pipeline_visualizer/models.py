"""Models for pipeline visualizer structures."""

from dataclasses import dataclass
from datetime import datetime

from .types import Delimiter


@dataclass(slots=True)
class Stage:
    """Represents a single stage in a pipeline.

    Attributes:
        command (str): The main command for this stage.
        subcommand (str | None): Optional subcommand.
        parameter (str | None): Optional parameter value.
        duration (datetime | None): Optional duration of the stage.
        throughput (float | None): Optional throughput value for the stage.
    """

    command: str
    subcommand: str | None = None
    parameter: str | None = None
    duration: datetime | None = None
    throughput: float | None = None


@dataclass(slots=True)
class Pipeline:
    """Represents the structure of a complete pipeline.

    Attributes:
        delimiter (Delimiter): The delimiter used to separate the left and right nodes of the pipeline.
        left (Stage | Pipeline): The left stage or nested pipeline.
        right (Stage | Pipeline): The right stage or nested pipeline.
    """

    delimiter: Delimiter
    left: "Stage | Pipeline"
    right: "Stage | Pipeline"

    def execute(self) -> None:
        """Execute the pipeline."""
        # Placeholder for execution logic


# @dataclass
# class PolishNotationPipeline:
#     pipeline: tuple[
#         Delimiter, "Stage | PolishNotationPipeline", "Stage | PolishNotationPipeline"
#     ]
