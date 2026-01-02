"""Daily entry command."""

import re
from datetime import date
from journal import config, parser, templates, ui, io
from .base import run_with_existing_check


def run(target_date: date = None):
    """Create a daily journal entry."""
    if target_date is None:
        target_date = date.today()

    filepath = config.daily_path(target_date)

    def create_daily_entry():
        print("=== Daily Journal Entry ===\n")

        # Get sleep hours
        sleep_hours = input("How many hours did you sleep last night? ").strip()

        # Get mindful eating moment (optional)
        print("\n--- Mindful Eating ---")
        mindful_eating = input("Describe one moment you ate mindfully yesterday (or press Enter to skip): ").strip()

        # Find weekly plan for freetime focuses
        weekly_path = config.weekly_path(target_date)
        freetime_focuses = []

        if weekly_path.exists():
            parsed = parser.parse_file(weekly_path)
            if parsed:
                freetime_focuses = parsed.get_list_items("freetime")

        # Create initial journal template using the template function
        content = templates.daily_journal_template(target_date, sleep_hours, freetime_focuses)

        # If mindful eating was provided, update the front matter
        if mindful_eating:
            content = re.sub(
                r'mindful_eating:',
                f'mindful_eating: {mindful_eating}',
                content
            )

        # Write initial file
        io.write_file(filepath, content)

        # Open in editor for user to write entry
        print("\nOpening editor for journal entry...")
        ui.open_in_editor(filepath)

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
        file_content = io.read_file(filepath)
        if file_content:
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

    run_with_existing_check(filepath, "Today's journal", create_daily_entry)
