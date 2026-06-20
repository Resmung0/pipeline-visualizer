"""Enums for pipeline visualizer.

This module defines string-based enumerations used across the
pipeline visualizer for delimiters, helper texts and arrow styles
with associated display symbols.
"""

from enum import StrEnum


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


class PipeArrow(StrEnum):
    """Represents the different arrow types used to visualize shell pipeline commands with the Pipe operator.

    The arrows are defined by strings, and the class provides a mechanism
    to map these string identifiers to specific Unicode symbols for
    visual representation.

    Attributes:
        STANDARD: Represents the standard arrow symbol used in visualizations.
        ALTERNATIVE: Represents the alternative arrow symbol used in visualizations.
        THICK: Represents the thick arrow symbol used in visualizations.
        TRIANGLE: Represents the triangle arrow symbol used in visualizations.
    """

    STANDARD = "→"
    ALTERNATIVE = "⇒"
    THICK = "──►"
    TRIANGLE = "▶"


class ConditionalORArrow(StrEnum):
    """Represents the different arrow types used to visualize shell pipeline commands with the Condition OR operator.

    The arrows are defined by strings, and the class provides a mechanism
    to map these string identifiers to specific Unicode symbols for
    visual representation.

    Attributes:
        STANDARD: Represents a standard arrow style.
        ALTERNATIVE: Represents an alternative arrow style.
        THICK: Represents a variation, often conceptually "thick" or an alternative appearance.
        TRIANGLE: Represents a variation, often appearing as a triangle arrow.
    """

    STANDARD = "↘"
    ALTERNATIVE = "⇘"
    THICK = "↘"
    TRIANGLE = "↘"


class ConditionalANDArrow(StrEnum):
    """Represents the different arrow types used to visualize shell pipeline commands with the Condition AND operator.

    The arrows are defined by strings, and the class provides a mechanism
    to map these string identifiers to specific Unicode symbols for
    visual representation.

    Attributes:
        STANDARD: Represents the standard arrow symbol used in visualizations.
        ALTERNATIVE: Represents the alternative arrow symbol used in visualizations.
        THICK: Represents the thick arrow symbol used in visualizations.
        TRIANGLE: Represents the triangle arrow symbol used in visualizations.
    """

    STANDARD = "↓"
    ALTERNATIVE = "⇓"
    THICK = "⤓"
    TRIANGLE = "▼"
