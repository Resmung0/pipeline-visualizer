from enum import StrEnum, auto


class HelperText(StrEnum):
    PIPELINE = "The shell pipeline command to visualize"
    ARROW = "Arrow type to use in the visualization (standard, alternative, or thick)"


class Arrows(StrEnum):
    STANDARD = auto()
    ALTERNATIVE = auto()
    THICK = auto()

    @property
    def symbol(self) -> str:
        """Returns the symbol corresponding to the arrow type."""
        symbols = {"standard": "→", "alternative": "⇒", "thick": "──►"}
        return symbols[self.value]
