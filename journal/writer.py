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
    subprocess.run([config.EDITOR, str(filepath)])


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
