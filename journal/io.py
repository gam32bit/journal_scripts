"""
File I/O operations.
Reading and writing journal files.
"""

import re
from pathlib import Path
from . import config


def write_file(filepath: Path, content: str) -> None:
    """Write content to file, creating directories as needed."""
    config.ensure_dir(filepath)
    filepath.write_text(content, encoding="utf-8")
    print(f"Created: {filepath}")


def read_file(filepath: Path) -> str | None:
    """Read file content, returning None if file doesn't exist."""
    if not filepath.exists():
        return None
    try:
        return filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return None


def extract_weekly_file_path(daily_file: Path) -> Path | None:
    """Extract weekly file path from daily file's reference."""
    content = read_file(daily_file)
    if not content:
        return None

    # Look for [weekly_file:/path/to/file]
    match = re.search(r"\[weekly_file:([^\]]+)\]", content)
    if match:
        path_str = match.group(1).strip()
        if path_str:
            return Path(path_str)

    return None
