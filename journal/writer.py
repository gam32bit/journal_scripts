"""
Writer for journal files.
Handles file creation and syncing completed tasks.
"""

import re
import subprocess
from pathlib import Path
from datetime import date

from . import config
from . import parser


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


def write_file(filepath: Path, content: str) -> None:
    """Write content to file, creating directories as needed."""
    config.ensure_dir(filepath)
    filepath.write_text(content, encoding="utf-8")
    print(f"Created: {filepath}")


def extract_weekly_file_path(daily_file: Path) -> Path | None:
    """Extract weekly file path from daily file's reference."""
    if not daily_file.exists():
        return None
    
    content = daily_file.read_text(encoding="utf-8")
    
    # Look for [weekly_file:/path/to/file]
    match = re.search(r"\[weekly_file:([^\]]+)\]", content)
    if match:
        path_str = match.group(1).strip()
        if path_str:
            return Path(path_str)
    
    return None
