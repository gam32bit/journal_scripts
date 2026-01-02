#!/usr/bin/env python3
"""
Weekly Plan - Create weekly planning template.
Run on Sundays to set up your week.
"""

import sys
from datetime import date
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, templates, writer


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
    print("(Press Ctrl+D or Ctrl+Z when finished)")

    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    return "\n".join(lines).strip()


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

    # What's coming up this week?
    coming_up = get_multi_line_input("What's coming up this week?")

    # How do you want to approach this week?
    approach = get_multi_line_text("\nHow do you want to approach this week?")

    # Freetime focuses
    freetime = get_multi_line_input("\nWhat are your freetime focuses for this week?")

    # Eating intention
    print("\n--- Eating Intention ---")
    eating_intention = input("Enter your eating intention for this week: ").strip()

    # Create the weekly plan content
    content = templates.weekly_plan_template(sunday, coming_up, approach, freetime, eating_intention)

    # Write the file
    writer.write_file(filepath, content)
    print(f"\nWeekly plan saved to: {filepath}")


if __name__ == "__main__":
    main()
