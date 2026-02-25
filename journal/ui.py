"""
User interaction utilities.
Prompts, menus, and editor integration.
"""

import subprocess
import sys
import threading
from pathlib import Path
from . import config


def start_background_timer(minutes=15):
    """Start a background timer that sends a desktop notification when time is up.

    Args:
        minutes: Number of minutes to wait before firing the notification.

    Returns:
        The threading.Timer object so it can be cancelled.
    """
    def _fire():
        result = subprocess.run(
            ["notify-send", "Journal Timer", f"{minutes} minutes have passed."],
            check=False
        )
        if result.returncode != 0:
            # Fallback: terminal bell
            sys.stderr.write("\a")
            sys.stderr.flush()

    timer = threading.Timer(minutes * 60, _fire)
    timer.daemon = True
    timer.start()
    return timer


def cancel_timer(timer):
    """Cancel a background timer if it hasn't fired yet."""
    timer.cancel()


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


def open_in_editor(filepath: Path, daily_entry: bool = False, timer_minutes: int = 0) -> None:
    """Open file in user's editor.

    Args:
        filepath: Path to the file to edit
        daily_entry: If True, position cursor after "Journal entry:" header
        timer_minutes: If nonzero, start a background timer for this many minutes
    """
    editor = config.EDITOR

    timer = None
    if timer_minutes:
        timer = start_background_timer(timer_minutes)

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

    if timer is not None:
        cancel_timer(timer)


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
