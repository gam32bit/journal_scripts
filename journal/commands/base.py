"""Base utilities for commands."""

from pathlib import Path
from journal import ui


def run_with_existing_check(filepath: Path, file_type: str, create_fn):
    """
    Standard flow: check if file exists, handle accordingly, then create.

    Args:
        filepath: Target file path
        file_type: Human-readable description for prompts
        create_fn: Callable that creates the file content and writes it
    """
    if filepath.exists():
        action = ui.handle_existing_file(filepath, file_type)
        if action != 'recreate':
            return

    create_fn()
