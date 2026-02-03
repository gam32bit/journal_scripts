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


def open_in_editor(filepath: Path, daily_entry: bool = False) -> None:
    """Open file in user's editor.

    Args:
        filepath: Path to the file to edit
        daily_entry: If True, position cursor after "Journal entry:" header
    """
    editor = config.EDITOR

    if editor in ('vim', 'nvim', 'vi'):
        if daily_entry:
            # Position cursor on line after "Journal entry:" and start in insert mode
            subprocess.run([
                editor,
                "+/Journal entry:/+1",
                "-c", "startinsert",
                str(filepath)
            ])
        else:
            # Default: open at end of file
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
