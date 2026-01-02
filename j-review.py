#!/usr/bin/env python3
"""
Weekly Review - Aggregate data from the week into a review document.
Run on Saturdays to reflect on your week.
"""

import sys
from datetime import date
from pathlib import Path
from collections import Counter

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, parser, writer


def calculate_sleep_average(hours: list[float]) -> float:
    """Calculate average sleep hours."""
    if not hours:
        return 0.0
    return sum(hours) / len(hours)


def print_sleep_table(week_dates, day_names):
    """Print a table of sleep hours for the week."""
    print("\n=== Sleep Log ===")

    # Collect sleep data
    sleep_hours = []
    for d in week_dates[1:6]:  # Monday through Friday (skip Sunday)
        daily_path = config.daily_path(d)
        parsed = parser.parse_file(daily_path)
        if parsed:
            hours_str = parsed.get_sleep_hours()
            if hours_str:
                try:
                    sleep_hours.append((d.strftime("%a"), float(hours_str)))
                except ValueError:
                    sleep_hours.append((d.strftime("%a"), None))
            else:
                sleep_hours.append((d.strftime("%a"), None))
        else:
            sleep_hours.append((d.strftime("%a"), None))

    # Calculate average
    valid_hours = [h for _, h in sleep_hours if h is not None]
    avg = calculate_sleep_average(valid_hours) if valid_hours else 0.0

    # Print header
    print(f"{'Sleep':<10}", end="")
    for day, _ in sleep_hours:
        print(f"{day:>8}", end="")
    print(f"{'Average':>10}")

    # Print values
    print(f"{'Hours':<10}", end="")
    for _, hours in sleep_hours:
        if hours is not None:
            print(f"{hours:>8.1f}", end="")
        else:
            print(f"{'  -':>8}", end="")
    print(f"{avg:>10.1f}" if avg > 0 else f"{'  -':>10}")


def print_tags_table(week_dates):
    """Print a table of tags for the week."""
    print("\n=== Emotional Tags ===")

    # Collect tag data
    tag_counter = Counter()
    tag_days = {}  # tag -> set of day indices

    for i, d in enumerate(week_dates[1:6]):  # Monday through Friday (skip Sunday)
        daily_path = config.daily_path(d)
        parsed = parser.parse_file(daily_path)
        if parsed:
            tags = parsed.get_tags()
            tag_counter.update(tags)
            for tag in tags:
                if tag not in tag_days:
                    tag_days[tag] = set()
                tag_days[tag].add(i)

    if not tag_counter:
        print("No tags recorded this week.")
        return

    # Sort by frequency
    sorted_tags = tag_counter.most_common()

    # Print header
    day_abbrev = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    print(f"{'Tag':<15}", end="")
    for day in day_abbrev:
        print(f"{day:>6}", end="")
    print()

    # Print separator
    print("-" * 50)

    # Print each tag
    for tag, count in sorted_tags:
        print(f"{tag:<15}", end="")
        for i in range(5):
            if i in tag_days.get(tag, set()):
                print(f"{'✓':>6}", end="")
            else:
                print(f"{'':>6}", end="")
        print()


def main():
    today = date.today()
    filepath = config.review_path(today)

    # Check if already exists
    if filepath.exists():
        action = writer.handle_existing_file(filepath, "Weekly review")
        if action != 'recreate':
            return

    print("=== Weekly Review ===\n")

    # Get week dates
    week_dates = config.get_week_dates(today)
    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # Find weekly plan
    weekly_path = config.weekly_path(today)

    # Print sleep table
    print_sleep_table(week_dates, day_names)

    # Print tags table
    print_tags_table(week_dates)

    # Get focus areas from weekly plan
    focus_areas = []
    if weekly_path.exists():
        parsed = parser.parse_file(weekly_path)
        if parsed:
            focus_areas = parsed.get_list_items("focus")

    # Print focus areas and ask for reflection
    print("\n=== Focus Areas ===")
    if focus_areas:
        for i, area in enumerate(focus_areas, 1):
            print(f"{i}. {area}")
    else:
        print("No focus areas defined for this week.")

    print("\n--- Reflection ---")
    reflection = input("How did you do with your focus areas this week? ")

    # Save the review
    content = f"""# Weekly Review
Week ending: {today.strftime("%B %d, %Y")}

## Focus Reflection:
{reflection}

"""

    writer.write_file(filepath, content)
    print(f"\nWeekly review saved to: {filepath}")


if __name__ == "__main__":
    main()
