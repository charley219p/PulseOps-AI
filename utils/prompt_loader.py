from pathlib import Path


def load_prompt(filename: str) -> str:
    return Path("prompts", filename).read_text(encoding="utf-8")