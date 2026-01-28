"""
Configuration for journal system.
Paths, constants, and editor settings.
"""

import os
from pathlib import Path
from datetime import date, timedelta


# Base directory for all journal files
JOURNAL_DIR = Path.home() / ".entries_encrypted/"

# Editor: respect $EDITOR, fall back to vim
EDITOR = os.environ.get("EDITOR", "vim")


def get_sunday(d: date) -> date:
    """Get the Sunday that starts the week containing date d."""
    # weekday(): Monday=0, Sunday=6
    # We want Sunday as start of week
    days_since_sunday = (d.weekday() + 1) % 7
    return d - timedelta(days=days_since_sunday)


def get_week_dates(d: date) -> list[date]:
    """Get all dates (Sun-Sat) for the week containing date d."""
    sunday = get_sunday(d)
    return [sunday + timedelta(days=i) for i in range(7)]


def _journal_path(d: date, prefix: str, ext: str = "md") -> Path:
    """Build path: JOURNAL_DIR/YYYY/MM/{prefix}-YYYY-MM-DD.{ext}"""
    return JOURNAL_DIR / f"{d.year}" / f"{d.month:02d}" / f"{prefix}-{d}.{ext}"


def daily_path(d: date) -> Path:
    """Path for daily journal entry."""
    return _journal_path(d, "daily")


def weekly_path(d: date) -> Path:
    """Path for weekly plan (uses Sunday of that week)."""
    sunday = get_sunday(d)
    return _journal_path(sunday, "weekly")


def review_path(d: date) -> Path:
    """Path for weekly review (uses Saturday of that week)."""
    saturday = get_sunday(d) + timedelta(days=6)
    return _journal_path(saturday, "review")


def monthly_path(d: date) -> Path:
    """Path for monthly review."""
    return JOURNAL_DIR / f"{d.year}" / f"{d.month:02d}" / f"monthly-{d.year}-{d.month:02d}.md"


def monthly_plan_path(d: date) -> Path:
    """Path for monthly plan."""
    return JOURNAL_DIR / f"{d.year}" / f"{d.month:02d}" / f"monthly-plan-{d.year}-{d.month:02d}.md"


def ensure_dir(filepath: Path) -> None:
    """Create parent directories if they don't exist."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
