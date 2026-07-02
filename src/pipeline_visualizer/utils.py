"""Utility helpers for pipeline visualizer shell parsing.

This module provides functions to extract shell operator and redirection
delimiter symbols from the corresponding enums.
"""

from typing import Literal

from .enums import Operator, Redirect


def extract_delimiters() -> list[Literal["|", "&&", "||", ";", ">", ">>", "<", "<<"]]:
    """Return shell operator and redirection delimiters.

    Returns:
        list[Literal["|", "&&", "||", ";", ">", ">>", "<", "<<"]]: The
        delimiters are extracted from the Operator and Redirect enums by
        filtering the enum members and collecting their symbol values.
    """
    extracted_delimiters = []
    for delimiters in Operator, Redirect:
        for delimiter in filter(lambda s: s.isupper(), dir(delimiters)):
            delimiter_symbol = delimiters[delimiter].value
            extracted_delimiters.append(delimiter_symbol)
    return extracted_delimiters
