"""Utility helpers for pipeline visualizer shell parsing.

This module provides functions to extract shell operator and redirection
delimiter symbols from the corresponding enums.
"""

from typing import Literal

from .enums import Operator, Redirect

Delimiter = Literal["|", "&&", "||", ";", ">", ">>", "<", "<<"]


def extract_delimiters() -> list[Delimiter]:
    """Return shell operator and redirection delimiters.

    Returns:
        list[Delimiter]: The delimiters extracted from the Operator and
        Redirect enums by collecting their symbol values.
    """
    return [member.value for enum in (Operator, Redirect) for member in enum]
