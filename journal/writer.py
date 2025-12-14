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


def sync_completed_tasks(daily_file: Path, weekly_file: Path) -> list[str]:
    """
    Read checked tasks from daily file and mark them complete in weekly file.
    Returns list of newly completed task names.
    """
    if not daily_file.exists() or not weekly_file.exists():
        return []
    
    # Parse daily file to get checked tasks
    daily = parser.parse_file(daily_file)
    if not daily:
        return []
    
    checked, _ = daily.get_checked_items("tasks_remaining")
    if not checked:
        return []
    
    # Read weekly file
    weekly_content = weekly_file.read_text(encoding="utf-8")
    
    # Parse to get already completed tasks
    weekly = parser.parse_file(weekly_file)
    if not weekly:
        return []
    
    already_completed = set()
    for line in weekly.get_section("completed"):
        stripped = line.strip()
        if stripped:
            already_completed.add(stripped)
    
    # Find newly completed tasks
    newly_completed = []
    for task in checked:
        if task not in already_completed:
            newly_completed.append(task)
    
    if not newly_completed:
        return []
    
    # Add to completed section in weekly file
    # Find [completed_tasks] marker and append after it
    lines = weekly_content.split("\n")
    new_lines = []
    found_completed = False
    
    for line in lines:
        new_lines.append(line)
        if "[completed_tasks]" in line.lower():
            found_completed = True
            # Add newly completed tasks right after this line
            for task in newly_completed:
                new_lines.append(task)
    
    if not found_completed:
        # Add section at end if not found
        new_lines.append("")
        new_lines.append("[completed_tasks]")
        for task in newly_completed:
            new_lines.append(task)
    
    # Also mark tasks as [x] in the tasks section
    updated_content = "\n".join(new_lines)
    for task in newly_completed:
        # Replace "- [ ] task" with "- [x] task" in tasks section
        pattern = rf"^(- \[)\s*(\] {re.escape(task)})$"
        updated_content = re.sub(
            pattern,
            r"\1x\2",
            updated_content,
            flags=re.MULTILINE
        )
    
    weekly_file.write_text(updated_content, encoding="utf-8")
    
    return newly_completed


def get_remaining_tasks(weekly_file: Path) -> list[str]:
    """Get tasks that haven't been completed yet."""
    parsed = parser.parse_file(weekly_file)
    if not parsed:
        return []
    
    # Get all tasks
    _, all_tasks = parsed.get_checked_items("tasks")
    checked_tasks, _ = parsed.get_checked_items("tasks")
    
    # Get completed tasks from completed section
    completed = set()
    for line in parsed.get_section("completed"):
        stripped = line.strip()
        if stripped:
            completed.add(stripped)
    
    # Also add checked tasks
    completed.update(checked_tasks)
    
    # Filter to remaining
    remaining = [t for t in all_tasks if t not in completed]
    
    return remaining


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
