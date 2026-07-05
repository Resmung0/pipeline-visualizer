"""File responsible to store types."""

from typing import Annotated, Literal

from cyclopts import Parameter

from .enums import (
    DiagonalArrow,
    HorizontalArrow,
    Operator,
    Redirect,
    VerticalArrow,
)
from .validations import validate_cmd

type ArrowStyle = Literal["standard", "alternative", "triangle"]
type Arrow = HorizontalArrow | VerticalArrow | DiagonalArrow
type Delimiter = Operator | Redirect
type PipelineCommand = Annotated[str, Parameter(validator=validate_cmd)]
