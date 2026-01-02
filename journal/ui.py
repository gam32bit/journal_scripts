"""
User interaction utilities.
Prompts, menus, and editor integration.
"""

import subprocess
from pathlib import Path
from . import config


def get_multi_line_input(prompt: str) -> list[str]:
    """Get multi-line bullet point input from user."""
    print(f"\n{prompt}")
    print("(Enter bullet points one per line, press Enter on empty line to finish)")

    items = []
    while True:
        line = input("- ").strip()
        if not line:
            break
        items.append(line)

    return items


def get_multi_line_text(prompt: str) -> str:
    """Get multi-line freeform text from user."""
    print(f"\n{prompt}")
    print("(Press Ctrl+D or Ctrl+Z when finished)")

    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    return "\n".join(lines).strip()


def open_in_editor(filepath: Path) -> None:
    """Open file in user's editor."""
    editor = config.EDITOR

    # For vim/nvim, open in insert mode at the end of the file
    if editor in ('vim', 'nvim', 'vi'):
        subprocess.run([editor, "+$", str(filepath)])
    else:
        subprocess.run([editor, str(filepath)])


def handle_existing_file(filepath: Path, file_type: str) -> str:
    """
    Handle case where file already exists.

    Args:
        filepath: Path to the existing file
        file_type: Human-readable description (e.g., "Weekly plan", "Today's journal")

    Returns: 'edit', 'recreate', or 'quit'
    """
    print(f"{file_type} already exists: {filepath}")
    choice = input("(e)dit in editor, (r)ecreate, or (q)uit? ").strip().lower()

    if choice == 'e':
        open_in_editor(filepath)
        return 'edit'
    elif choice == 'r':
        return 'recreate'
    else:
        return 'quit'
