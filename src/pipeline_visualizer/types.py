from __future__ import annotations

from typing import TypedDict

from .enums import Delimiter


class Pipeline(TypedDict):
    delimiter: Delimiter | None
    stages: list[str | Pipeline]
