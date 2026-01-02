#!/usr/bin/env python3
"""
Daily Journal - Create daily journal entry.
"""

import sys
import re
from datetime import date
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, parser, templates, writer


def main():
    today = date.today()
    filepath = config.daily_path(today)

    # Check if already exists
    if filepath.exists():
        action = writer.handle_existing_file(filepath, "Today's journal")
        if action != 'recreate':
            return

    print("=== Daily Journal Entry ===\n")

    # Get sleep hours
    sleep_hours = input("How many hours did you sleep last night? ").strip()

    # Get mindful eating moment (optional)
    print("\n--- Mindful Eating ---")
    mindful_eating = input("Describe one moment you ate mindfully yesterday (or press Enter to skip): ").strip()

    # Find weekly plan for freetime focuses
    weekly_path = config.weekly_path(today)
    freetime_focuses = []

    if weekly_path.exists():
        parsed = parser.parse_file(weekly_path)
        if parsed:
            freetime_focuses = parsed.get_list_items("freetime")

    # Create initial journal template using the template function
    content = templates.daily_journal_template(today, sleep_hours, freetime_focuses)

    # If mindful eating was provided, update the front matter
    if mindful_eating:
        content = re.sub(
            r'mindful_eating:',
            f'mindful_eating: {mindful_eating}',
            content
        )

    # Write initial file
    writer.write_file(filepath, content)

    # Open in editor for user to write entry
    print("\nOpening editor for journal entry...")
    writer.open_in_editor(filepath)

    # After editor closes, prompt for summary bullets
    print("\n--- Summary Bullets ---")
    print("Add 2-3 summary bullets that capture the texture of today")
    print("(e.g., 'Fun family visit', 'Weird unexplained lethargy')")
    print("(Enter bullet points one per line, press Enter on empty line to finish)")

    summary_bullets = []
    while True:
        bullet = input("- ").strip()
        if not bullet:
            break
        summary_bullets.append(bullet)

    # Read the current file content
    if filepath.exists():
        file_content = filepath.read_text(encoding="utf-8")

        # Update the summary section
        if summary_bullets:
            bullets_str = "\n".join(f"- {bullet}" for bullet in summary_bullets)
            # Replace the empty summary section with the actual bullets
            file_content = re.sub(
                r'## Summary:\n-\n-',
                f'## Summary:\n{bullets_str}',
                file_content
            )

            filepath.write_text(file_content, encoding="utf-8")
            print(f"\nJournal entry saved with {len(summary_bullets)} summary bullets!")
        else:
            print("\nJournal entry saved (no summary bullets added).")
    else:
        print("\nWarning: Journal file not found.")


if __name__ == "__main__":
    main()
