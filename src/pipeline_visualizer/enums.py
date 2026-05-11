from enum import StrEnum, auto


class Delimiter(StrEnum):
    PIPE = "|"
    AND = "&&"
    OR = "||"
    REDIRECT_OUT = ">"
    REDIRECT_OUT_APPEND = ">>"
    REDIRECT_IN = "<"
    REDIRECT_IN_APPEND = "<<"


class HelperText(StrEnum):
    PIPELINE = "The shell pipeline command to visualize"
    ARROW = "Arrow type to use in the visualization"


class PipeArrow(StrEnum):
    STANDARD = auto()
    ALTERNATIVE = auto()
    THICK = auto()
    TRIANGLE = auto()

    @property
    def symbol(self) -> str:
        """Returns the symbol corresponding to arrow type."""
        symbols = {"standard": "→", "alternative": "⇒", "thick": "──►", "triangle": "▶"}
        return symbols[self.value]


class ConditionalORArrow(StrEnum):
    STANDARD = auto()
    ALTERNATIVE = auto()
    THICK = "standard"
    TRIANGLE = "standard"

    @property
    def symbol(self) -> str:
        """Returns the symbol corresponding to arrow type"""
        symbols = {"standard": "↘", "alternative": "⇘"}
        return symbols[self.value]


class ConditionalANDArrow(StrEnum):
    STANDARD = auto()
    ALTERNATIVE = auto()
    THICK = auto()
    TRIANGLE = auto()

    @property
    def symbol(self) -> str:
        """Returns the symbol corresponding to arrow type."""
        symbols = {"standard": "↓", "alternative": "⇓", "thick": "⤓", "triangle": "▼"}
        return symbols[self.value]
