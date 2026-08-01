"""
Configuration for journal system.
Paths, constants, and editor settings.
"""

import calendar
import os
from collections import Counter
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


def week_owner(d: date) -> tuple[int, int]:
    """Get the (year, month) that owns the week containing date d.

    A week belongs to whichever month holds most of its seven days. A week
    spans at most two months, so there is always a strict majority.
    """
    counts = Counter((day.year, day.month) for day in get_week_dates(d))
    return counts.most_common(1)[0][0]


def last_week_end_of_month(year: int, month: int) -> date:
    """Get the Saturday ending the last week that belongs to the given month."""
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    saturday = get_sunday(last_day) + timedelta(days=6)
    if week_owner(saturday) != (year, month):
        saturday -= timedelta(days=7)
    return saturday


def detect_review_month(today: date = None) -> date:
    """Get the first of the most recent month whose weeks have all ended.

    Monthly reviews aggregate weekly reviews, so a month is only ready once
    every week belonging to it is over. Running this on Aug 1 targets July,
    not the August that just started.
    """
    if today is None:
        today = date.today()

    year, month = week_owner(today)
    while last_week_end_of_month(year, month) > today:
        year, month = (year - 1, 12) if month == 1 else (year, month - 1)

    return date(year, month, 1)


def _journal_path(d: date, prefix: str, ext: str = "md") -> Path:
    """Build path: JOURNAL_DIR/YYYY/MM/{prefix}-YYYY-MM-DD.{ext}"""
    return JOURNAL_DIR / f"{d.year}" / f"{d.month:02d}" / f"{prefix}-{d}.{ext}"


def daily_path(d: date) -> Path:
    """Path for daily journal entry."""
    return _journal_path(d, "daily")


def review_path(d: date) -> Path:
    """Path for weekly review (uses Saturday of that week)."""
    saturday = get_sunday(d) + timedelta(days=6)
    return _journal_path(saturday, "review")


def monthly_path(d: date) -> Path:
    """Path for monthly review."""
    return JOURNAL_DIR / f"{d.year}" / f"{d.month:02d}" / f"monthly-{d.year}-{d.month:02d}.md"


def ensure_dir(filepath: Path) -> None:
    """Create parent directories if they don't exist."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
