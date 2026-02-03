"""
File I/O operations.
Reading and writing journal files.
"""

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
