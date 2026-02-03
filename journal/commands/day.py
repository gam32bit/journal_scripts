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

        # Get thoughts on eating
        mindful_eating = input("Thoughts on eating yesterday? ").strip()

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

        # Open in editor for user to write entry (position cursor at journal entry)
        print("\nOpening editor for journal entry...")
        ui.open_in_editor(filepath, daily_entry=True)

        # Read the file content to show the user what they wrote
        saved_content = io.read_file(filepath)
        if saved_content:
            # Parse to get the journal entry section
            parsed = parser.parse_file(filepath)
            if parsed:
                journal_text = parsed.get_section_text("journal")
                if journal_text:
                    print("\n=== Your journal entry ===")
                    print(journal_text)
                    print("=" * 30)

        # Prompt for summary bullets
        summary_bullets = ui.get_multi_line_input("\nAdd summary bullets for this entry (or press Enter to skip):")

        # Append summary section if bullets were provided
        if summary_bullets:
            summary_section = "\n---\n\n## Summary:\n"
            for bullet in summary_bullets:
                summary_section += f"- {bullet}\n"

            with open(filepath, "a", encoding="utf-8") as f:
                f.write(summary_section)
            print("\nSummary added to journal entry!")
        else:
            print("\nJournal entry saved!")

    run_with_existing_check(filepath, "Today's journal", create_daily_entry)
