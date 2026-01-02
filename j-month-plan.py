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

    print("\nOpening monthly plan template in vim...")
    print("Fill in the sections and save when done.\n")

    # Create the monthly plan template with empty sections
    content = templates.monthly_plan_template(today, [], "", [])

    # Write the template file
    writer.write_file(filepath, content)

    # Open in vim for editing
    writer.open_in_editor(filepath)

    print(f"\nMonthly plan saved to: {filepath}")


if __name__ == "__main__":
    main()
