"""Utility helpers for pipeline visualizer shell parsing.

This module provides functions to extract shell operator and redirection
delimiter symbols from the corresponding enums.
"""

from .enums import DelimiterSymbol, Operator, Redirect


def extract_delimiters() -> tuple[DelimiterSymbol, ...]:
    """Return shell operator and redirection delimiters.

    The delimiters are returned in the order they are defined in the
    Operator and Redirect enums.

    Returns:
        tuple[DelimiterSymbol, ...]: The delimiters extracted from the
        Operator and Redirect enums by collecting their symbol values.
    """
    return tuple(member.value for enum in (Operator, Redirect) for member in enum)
