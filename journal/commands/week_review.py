"""Weekly review command."""

from datetime import date
from journal import config, parser, templates, ui, io
from .base import run_with_existing_check


def run(target_date: date = None):
    """Create a weekly review."""
    if target_date is None:
        target_date = date.today()

    filepath = config.review_path(target_date)

    def create_weekly_review():
        print("=== Weekly Review ===\n")

        week_dates = config.get_week_dates(target_date)

        print("=== Daily Entries ===")
        daily_entries = {}

        for d in week_dates:
            daily_path = config.daily_path(d)
            if daily_path.exists():
                parsed = parser.parse_file(daily_path)
                if parsed:
                    journal_text = parsed.get_section_text("journal")
                    if journal_text:
                        label = d.strftime("%A, %B %d")
                        daily_entries[label] = journal_text
                        print(f"\n{'-' * 40}")
                        print(label)
                        print(journal_text)

        if not daily_entries:
            print("  (No daily entries found)")

        print("\n=== Weekly Reflection ===")
        weekly_reflection = input("How did this week go? ").strip()

        weekly_summary = ui.get_multi_line_input(
            "\n=== Weekly Summary ===\nWrite 3-5 bullets synthesizing the week:"
        )

        content = templates.weekly_review_template(
            d=target_date,
            daily_entries=daily_entries,
            weekly_reflection=weekly_reflection,
            weekly_summary=weekly_summary,
        )

        # Write the file
        io.write_file(filepath, content)
        print(f"\nWeekly review saved to: {filepath}")

    run_with_existing_check(filepath, "Weekly review", create_weekly_review)
