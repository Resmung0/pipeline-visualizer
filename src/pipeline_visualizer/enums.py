"""Enums for pipeline visualizer.

This module defines string-based enumerations used across the
pipeline visualizer for delimiters, helper texts and arrow styles
with associated display symbols.
"""

from enum import StrEnum, auto
from typing import Literal


class Operator(StrEnum):
    """Supported delimiters used in pipeline commands.

    Attributes:
        PIPE: Pipe symbol for command chaining (e.g., `|` in Bash).
        AND: Logical AND operator (e.g., `&&` in Bash).
        OR: Logical OR operator (e.g., `||` in Bash).
    """

    PIPE = "|"
    AND = "&&"
    OR = "||"
    SEMICOLON = ";"


class Redirect(StrEnum):
    """Redirections used in pipeline commands.

    Attributes:
        REDIRECT_OUT: Redirect output to a file.
        REDIRECT_OUT_APPEND: Append redirect output to a file.
        REDIRECT_IN: Input redirection from a file.
        REDIRECT_IN_APPEND: Append input redirection from a file.
    """

    OUT = ">"
    OUT_APPEND = ">>"
    IN = "<"
    IN_APPEND = "<<"


class HelperText(StrEnum):
    """Provides descriptive text hints for the shell visualization process.

    Attributes:
        PIPELINE: Descriptive text for the overall pipeline command visualization.
        ARROW: Descriptive text for the arrow type selection in the visualization.
    """

    PIPELINE = "The shell pipeline command to visualize"
    ARROW = "Arrow type to use in the visualization"


class PipeArrow(StrEnum):
    """Represents the different arrow types used to visualize shell pipeline commands.

    Attributes:
        STANDARD: Represents the standard arrow symbol used in visualizations.
        ALTERNATIVE: Represents the alternative arrow symbol used in visualizations.
        THICK: Represents the thick arrow symbol used in visualizations.
        TRIANGLE: Represents the triangle arrow symbol used in visualizations.
    """

    STANDARD = auto()
    ALTERNATIVE = auto()
    THICK = auto()
    TRIANGLE = auto()

    @property
    def symbol(self) -> str:
        """Symbol corresponding to arrow type.

        Returns:
            str: The Unicode symbol for the arrow.

        Raises:
            KeyError: If the enum's value is not recognized in the symbol mapping.
        """
        symbols = {"standard": "→", "alternative": "⇒", "thick": "──►", "triangle": "▶"}
        return symbols[self.value]

    @property
    def color(self) -> Literal["bold yellow"]:
        """The collor of the arrow.

        Returns:
            Literal["bold yellow"]: Arrow with a yellow color.
        """
        return "bold yellow"


class ConditionalORArrow(StrEnum):
    """Represents various conditional or logical OR arrow types.

    The arrows are defined by strings, and the class provides a mechanism
    to map these string identifiers to specific Unicode symbols for
    visual representation in documents or UIs.

    Attributes:
        STANDARD (StrEnum): Represents a standard arrow style.
        ALTERNATIVE (StrEnum): Represents an alternative arrow style.
        THICK (StrEnum): Represents a variation, often conceptually "thick"
                         or an alternative appearance.
        TRIANGLE (StrEnum): Represents a variation, often appearing as a triangle arrow.
    """

    STANDARD = auto()
    ALTERNATIVE = auto()
    THICK = "standard"
    TRIANGLE = "standard"

    @property
    def symbol(self) -> str:
        """Returns the Unicode symbol corresponding to the arrow type.

        The symbol mapping is defined internally based on the enum's string value.
        Note that the 'symbol' will only return defined values, and any
        unmapped value will raise a KeyError.

        Returns:
            str: The Unicode symbol for the arrow.

        Raises:
            KeyError: If the enum's value is not recognized in the symbol mapping.
        """
        symbols = {"standard": "↘", "alternative": "⇘"}
        return symbols[self.value]

    @property
    def color(self) -> Literal["bold yellow"]:
        """The collor of the arrow.

        Returns:
            Literal["bold yellow"]: Arrow with a yellow color.
        """
        return "bold yellow"


class ConditionalANDArrow(StrEnum):
    """Represents various conditional or logical AND arrow types.

    Attributes:
        STANDARD: Represents the standard arrow symbol used in visualizations.
        ALTERNATIVE: Represents the alternative arrow symbol used in visualizations.
        THICK: Represents the thick arrow symbol used in visualizations.
        TRIANGLE: Represents the triangle arrow symbol used in visualizations.
    """

    STANDARD = auto()
    ALTERNATIVE = auto()
    THICK = auto()
    TRIANGLE = auto()

    @property
    def symbol(self) -> str:
        """Returns the symbol corresponding to arrow type.

        Returns:
            str: The Unicode symbol for the arrow.

        Raises:
            KeyError: If the enum's value is not recognized in the symbol mapping.
        """
        symbols = {"standard": "↓", "alternative": "⇓", "thick": "⤓", "triangle": "▼"}
        return symbols[self.value]

    @property
    def color(self) -> Literal["bold yellow"]:
        """The collor of the arrow.

        Returns:
            Literal["bold yellow"]: Arrow with a yellow color.
        """
        return "bold yellow"
