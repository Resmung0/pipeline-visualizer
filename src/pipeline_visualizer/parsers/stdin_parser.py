import shlex


def parse(cmd: str) -> list[list[str]]:
    stages = cmd.split("|")
    return [shlex.split(stage.strip()) for stage in stages]
