"""Enums for pipeline visualizer.

This module defines string-based enumerations used across the
pipeline visualizer for delimiters, helper texts and arrow styles
with associated display symbols.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .types import ArrowStyle


class HorizontalArrow(StrEnum):
    """Represents the different arrow types on horizontal orientation used to visualize shell pipeline commands.

    The arrows are defined by strings, and the class provides a mechanism
    to map these string identifiers to specific Unicode symbols for visual representation.

    Attributes:
        STANDARD: Represents the standard arrow symbol used in visualizations.
        ALTERNATIVE: Represents the alternative arrow symbol used in visualizations.
        TRIANGLE: Represents the triangle arrow symbol used in visualizations.
    """

    STANDARD = "→"
    ALTERNATIVE = "⇒"
    TRIANGLE = "▶"


class DiagonalArrow(StrEnum):
    """Represents the different arrow types on diagonal orientation used to visualize shell pipeline commands.

    The arrows are defined by strings, and the class provides a mechanism
    to map these string identifiers to specific Unicode symbols for visual representation.

    Attributes:
        STANDARD: Represents a standard arrow style.
        ALTERNATIVE: Represents an alternative arrow style.
        TRIANGLE: Represents a variation, often appearing as a triangle arrow.
    """

    STANDARD = "↘"
    ALTERNATIVE = "⇘"
    TRIANGLE = "↘"


class VerticalArrow(StrEnum):
    """Represents the different arrow types on vertical orientation used to visualize shell pipeline commands.

    The arrows are defined by strings, and the class provides a mechanism
    to map these string identifiers to specific Unicode symbols for visual representation.

    Attributes:
        STANDARD: Represents the standard arrow symbol used in visualizations.
        ALTERNATIVE: Represents the alternative arrow symbol used in visualizations.
        TRIANGLE: Represents the triangle arrow symbol used in visualizations.
    """

    STANDARD = "↓"
    ALTERNATIVE = "⇓"
    TRIANGLE = "▼"


class Operator(StrEnum):
    """Supported delimiters used in pipeline commands.

    Attributes:
        PIPE: Pipe symbol for command chaining in Bash (e.g., `|`).
        AND: Logical AND operator in Bash (e.g., `&&`).
        OR: Logical OR operator in Bash (e.g., `||`).
        SEMICOLON: Break of line operator in Bash (e.g., `;`).
    """

    PIPE = "|"
    AND = "&&"
    OR = "||"
    SEMICOLON = ";"

    def arrow_style(self, style: ArrowStyle) -> str:
        """Return the style associated with the operator.

        Args:
            style (ArrowStyle): The style name to retrieve the corresponding arrow.

        Returns:
            str: The style name corresponding to the operator.
        """
        arrow_style = style.upper()
        match self:
            case Operator.AND | Operator.SEMICOLON:
                arrow = HorizontalArrow[arrow_style]
            case Operator.PIPE:
                arrow = VerticalArrow[arrow_style]
            case Operator.OR:
                arrow = DiagonalArrow[arrow_style]
        return str(arrow)

    def is_horizontal(self) -> bool:
        """Check if the operator is horizontal.

        Returns:
            bool: True if the operator is horizontal, False otherwise.
        """
        return self in {Operator.AND, Operator.OR, Operator.SEMICOLON}


class Redirect(StrEnum):
    """Redirections used in pipeline commands.

    Attributes:
        OUT: Redirect output to a file.
        OUT_APPEND: Append redirect output to a file.
        IN: Input redirection from a file.
        IN_APPEND: Append input redirection from a file.
    """

    OUT = ">"
    OUT_APPEND = ">>"
    IN = "<"
    IN_APPEND = "<<"

    def arrow_style(self, _: ArrowStyle) -> Literal[">", ">>", "<", "<<"]:
        """Return the style associated with the operator.

        Returns:
            Literal[">", ">>", "<", "<<"]: The style name corresponding to the operator.
        """
        return self.value

    def is_horizontal(self) -> bool:
        """Check if the operator is horizontal.

        Returns:
            bool: True if the operator is horizontal, False otherwise.
        """
        return False


class PipelineStatus(StrEnum):
    ERROR = "⊘"
    SUCCESS = "◆"
    PENDING = "◇"
    RUNNING = "◈"
    WARNING = "⚠"
    SKIPPED = "↻"


class StageStatus(StrEnum):
    ERROR = "⊘"
    SUCCESS = "●"
    PENDING = "○"
    RUNNING = "◉"
    WARNING = "⚠"
    SKIPPED = "↻"


class TreeConnector(StrEnum):
    connectors = "│"
    branch = "├─"
    last_branch = "└─"
