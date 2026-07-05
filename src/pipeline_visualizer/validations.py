"""Validation functions for pipeline commands."""

from pipeline_visualizer.utils import extract_delimiters


def validate_cmd(type_: str, value: str) -> None:  # noqa: ARG001
    """Validate that the provided command string contains a bash pipeline delimiter.

    Args:
        type_ (str): The type of command being validated.
        value (str): The command string to validate.

    Raises:
        ValueError: If the command string does not contain any recognized pipeline delimiters.
    """
    delimiters = extract_delimiters()
    if any(delimiter in value for delimiter in delimiters):
        return
    raise ValueError(
        f"This isn't a bash pipeline! Please use one of the following {delimiters=}"
    )
