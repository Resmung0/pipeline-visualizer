"""File responsible to store types."""

from typing import Literal

from .enums import (
    ConditionalANDArrow,
    ConditionalORArrow,
    Operator,
    PipeArrow,
    Redirect,
)

type ArrowStyle = Literal["standard", "alternative", "thick", "triangle"]
type Arrow = PipeArrow | ConditionalORArrow | ConditionalANDArrow
type Delimiter = Operator | Redirect | None
