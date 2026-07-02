"""File responsible to store types."""

from typing import Annotated, Literal

from cyclopts import Parameter

from .enums import (
    ConditionalANDArrow,
    ConditionalORArrow,
    Operator,
    PipeArrow,
    Redirect,
)
from .validations import validate_cmd

type ArrowStyle = Literal["standard", "alternative", "thick", "triangle"]
type Arrow = PipeArrow | ConditionalORArrow | ConditionalANDArrow
type Delimiter = Operator | Redirect | None
type PipelineCommand = Annotated[str, Parameter(validator=validate_cmd)]
