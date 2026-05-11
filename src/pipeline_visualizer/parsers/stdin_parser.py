from loguru import logger

from src.pipeline_visualizer.enums import Delimiter
from src.pipeline_visualizer.types import Pipeline


def _matches_delimiter(
    pipeline_cmd: str,
    char_id: int,
    delimiter: Delimiter,
) -> bool:
    if not pipeline_cmd.startswith(delimiter.value, char_id):
        return False

    if delimiter is Delimiter.PIPE:
        is_or_operator = pipeline_cmd.startswith(Delimiter.OR.value, char_id)
        is_second_or_char = char_id > 0 and pipeline_cmd[char_id - 1] == "|"
        return not (is_or_operator or is_second_or_char)

    return True


def _top_level_delimiters(
    pipeline_cmd: str,
    delimiters: tuple[Delimiter, ...],
) -> list[tuple[int, Delimiter]]:
    matches: list[tuple[int, Delimiter]] = []
    delimiters_by_size = sorted(
        delimiters,
        key=lambda delimiter: len(delimiter.value),
        reverse=True,
    )
    quote: str | None = None
    escaped = False
    group_depth = 0
    char_id = 0

    while char_id < len(pipeline_cmd):
        char = pipeline_cmd[char_id]

        if escaped:
            escaped = False
            char_id += 1
            continue

        if char == "\\" and quote != "'":
            escaped = True
            char_id += 1
            continue

        if quote:
            if char == quote:
                quote = None
            char_id += 1
            continue

        if char in ("'", '"', "`"):
            quote = char
            char_id += 1
            continue

        if char == "(":
            group_depth += 1
            char_id += 1
            continue

        if char == ")" and group_depth > 0:
            group_depth -= 1
            char_id += 1
            continue

        if group_depth == 0:
            for delimiter in delimiters_by_size:
                if _matches_delimiter(pipeline_cmd, char_id, delimiter):
                    matches.append((char_id, delimiter))
                    char_id += len(delimiter.value)
                    break
            else:
                char_id += 1
            continue

        char_id += 1

    return matches


def _split_pipeline(pipeline_cmd: str) -> list[str]:
    matches = _top_level_delimiters(pipeline_cmd, (Delimiter.PIPE,))
    if not matches:
        return [pipeline_cmd.strip()]

    stages: list[str] = []
    stage_start = 0
    for delimiter_id, delimiter in matches:
        stages.append(pipeline_cmd[stage_start:delimiter_id].strip())
        stage_start = delimiter_id + len(delimiter.value)

    stages.append(pipeline_cmd[stage_start:].strip())
    return stages


def _parse_conditionals(pipeline_cmd: str) -> str | Pipeline:
    matches = _top_level_delimiters(
        pipeline_cmd,
        (Delimiter.AND, Delimiter.OR),
    )
    if not matches:
        return pipeline_cmd.strip()

    delimiter_id, delimiter = matches[-1]
    left_stage = pipeline_cmd[:delimiter_id].strip()
    right_stage = pipeline_cmd[delimiter_id + len(delimiter.value) :].strip()

    return {
        "delimiter": delimiter,
        "stages": [
            _parse_conditionals(left_stage),
            _parse_conditionals(right_stage),
        ],
    }


@logger.catch
def parse(pipeline_cmd: str) -> Pipeline:
    stages = _split_pipeline(pipeline_cmd.strip())
    if len(stages) > 1:
        return {
            "delimiter": Delimiter.PIPE,
            "stages": [_parse_conditionals(stage) for stage in stages],
        }

    stage = _parse_conditionals(stages[0])
    if isinstance(stage, str):
        return {"delimiter": None, "stages": [stage]}

    return stage
