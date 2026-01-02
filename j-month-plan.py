#!/usr/bin/env python3
"""
Monthly Plan - Create monthly planning template.
Run at the beginning of each month to set up the month.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, parser, templates, writer


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


def get_multi_line_text(prompt: str) -> str:
    """Get multi-line freeform text from user."""
    print(f"\n{prompt}")
    print("(Press Ctrl+D or Ctrl+Z when finished, or press Enter on empty line to skip)")

    lines = []
    try:
        while True:
            line = input()
            if not line and not lines:
                # Empty line at the start - skip
                break
            lines.append(line)
    except EOFError:
        pass

    return "\n".join(lines).strip()


def get_last_month_summary(today: date) -> list[str]:
    """Get the monthly summary from last month's review."""
    # Get previous month
    first_of_month = today.replace(day=1)
    last_month = first_of_month - timedelta(days=1)

    monthly_review_path = config.monthly_path(last_month)
    if not monthly_review_path.exists():
        return []

    parsed = parser.parse_file(monthly_review_path)
    if not parsed:
        return []

    return parsed.get_list_items("monthly_summary")


def main():
    today = date.today()
    filepath = config.monthly_plan_path(today)

    # Check if already exists
    if filepath.exists():
        action = writer.handle_existing_file(filepath, "Monthly plan")
        if action != 'recreate':
            return

    print("=== Monthly Plan Setup ===\n")

    # Show last month's summary if available
    print("--- Last Month's Summary ---")
    last_month_summary = get_last_month_summary(today)
    if last_month_summary:
        for bullet in last_month_summary:
            print(f"  - {bullet}")
    else:
        print("  (No summary from last month)")

    # What's coming up this month?
    coming_up = get_multi_line_input("\nWhat's coming up this month? (big events, deadlines, trips)")

    # Themes or intentions (optional)
    themes = get_multi_line_text("\nThemes or intentions for this month (optional)?")

    # Freetime focuses to prioritize
    freetime = get_multi_line_input("\nWhat freetime focuses do you want to prioritize this month?")

    # Create the monthly plan content
    content = templates.monthly_plan_template(today, coming_up, themes, freetime)

    # Write the file
    writer.write_file(filepath, content)
    print(f"\nMonthly plan saved to: {filepath}")


if __name__ == "__main__":
    main()
