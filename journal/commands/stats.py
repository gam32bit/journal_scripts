"""Journal stats command."""

import calendar
from datetime import date
from journal import config
from .writing import scan_writings


def run(target_date: date = None):
    """Show journal and writing stats for the current month."""
    if target_date is None:
        target_date = date.today()

    year, month = target_date.year, target_date.month
    month_name = target_date.strftime("%B %Y")
    num_days = calendar.monthrange(year, month)[1]

    # Count daily journal entries
    daily_count = 0
    for day in range(1, num_days + 1):
        d = date(year, month, day)
        if config.daily_path(d).exists():
            daily_count += 1

    # Count writing pieces for the month
    date_strs = {
        date(year, month, day).strftime("%Y-%m-%d")
        for day in range(1, num_days + 1)
    }
    writings = scan_writings(date_strs)
    published_count = sum(1 for _, status, _, _ in writings if status == "published")
    draft_count = sum(1 for _, status, _, _ in writings if status == "draft")

    print(f"\n=== {month_name} ===")
    print(f"Journal entries: {daily_count} / {num_days} days")
    if writings:
        print(f"Writings: {len(writings)} ({published_count} published, {draft_count} draft)")
    else:
        print("Writings: 0")
