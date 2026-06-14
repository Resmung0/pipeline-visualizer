"""Models for pipeline visualizer structures."""

from collections.abc import Sequence
from typing import TypedDict

from .types import Delimiter


class Pipeline(TypedDict):
    """Represents the structure of a complete pipeline."""

    delimiter: Delimiter
    stages: Sequence["str | Pipeline"]


# @dataclass
# class Stage:
#     command: str
#     subcommand: str | None
#     parameter: str
#     duration: datetime
#     throughput: float


# @dataclass
# class AlternativePipeline:
#     delimiter: Delimiter
#     left: "Stage | AlternativePipeline"
#     right: "Stage | AlternativePipeline"

#     def execute(self):
#         pass


# @dataclass
# class PolishNotationPipeline:
#     pipeline: tuple[
#         Delimiter, "Stage | PolishNotationPipeline", "Stage | PolishNotationPipeline"
#     ]
