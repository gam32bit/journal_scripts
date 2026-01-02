#!/usr/bin/env python3
"""
Weekly Plan - Create weekly planning template.
Run on Sundays to set up your week.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, parser, writer


def get_past_week_eating_reflections(today: date) -> list[tuple[str, str]]:
    """Get eating reflections from the past week (Sun-Sat)."""
    # Get the previous week's dates
    last_week_sunday = config.get_sunday(today) - timedelta(days=7)
    last_week_dates = [last_week_sunday + timedelta(days=i) for i in range(7)]

    reflections = []
    for d in last_week_dates:
        daily_path = config.daily_path(d)
        parsed = parser.parse_file(daily_path)
        if parsed:
            text = parsed.get_section_text("eating")
            if text:
                reflections.append((d.strftime("%A, %B %d"), text))

    return reflections


def get_past_focus_reflection(today: date) -> str | None:
    """Get focus area reflection from the past weekly review."""
    # Get last week's Saturday (when review would have been done)
    last_saturday = config.get_sunday(today) - timedelta(days=1)
    review_path = config.review_path(last_saturday)

    if not review_path.exists():
        return None

    parsed = parser.parse_file(review_path)
    if not parsed:
        return None

    # Look for the focus reflection section
    reflection = parsed.get_section_text("reflection")
    return reflection if reflection else None


def main():
    today = date.today()
    sunday = config.get_sunday(today)
    filepath = config.weekly_path(today)

    # Check if already exists
    if filepath.exists():
        action = writer.handle_existing_file(filepath, "Weekly plan")
        if action != 'recreate':
            return

    print("=== Weekly Plan Setup ===\n")

    # Show eating reflections from past week
    print("--- Eating Reflections from Past Week ---")
    eating_reflections = get_past_week_eating_reflections(today)
    if eating_reflections:
        for day, reflection in eating_reflections:
            print(f"\n{day}:")
            print(f"  {reflection}")
    else:
        print("No eating reflections found from last week.")

    # Get eating intention for this week
    print("\n--- Weekly Eating Intention ---")
    eating_intention = input("Enter your eating intention for this week: ").strip()

    # Show focus reflection from past review
    print("\n--- Past Focus Area Reflection ---")
    past_reflection = get_past_focus_reflection(today)
    if past_reflection:
        print(past_reflection)
    else:
        print("No focus area reflection available from last week.")

    # Get focus areas for this week
    print("\n--- Focus Areas for This Week ---")
    focus_areas = []
    while True:
        if focus_areas:
            another = input("\nAdd another focus area? (y/n): ").strip().lower()
            if another != 'y':
                break

        focus = input("Enter a focus area (or press Enter to finish): ").strip()
        if not focus:
            break
        focus_areas.append(focus)

    # Create the weekly plan content
    focus_str = "\n".join(f"- {area}" for area in focus_areas) if focus_areas else "- "

    content = f"""# Weekly Plan
Week of: {sunday.strftime("%B %d, %Y")}

## Eating Intention:
{eating_intention}

## Focus areas:
{focus_str}

"""

    # Write the file
    writer.write_file(filepath, content)
    print(f"\nWeekly plan saved to: {filepath}")


if __name__ == "__main__":
    main()
