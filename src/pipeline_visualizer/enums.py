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
        """Retorna o símbolo correspondente ao tipo de arrow"""
        symbols = {"standard": "→", "alternative": "⇒", "thick": "──►"}
        return symbols[self.value]
