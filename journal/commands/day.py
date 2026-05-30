"""Daily entry command."""

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

        content = templates.daily_journal_template(target_date)
        io.write_file(filepath, content)

        print("\nOpening editor for journal entry...")
        ui.open_in_editor(filepath, daily_entry=True, timer_minutes=15)

        parsed = parser.parse_file(filepath)
        if parsed:
            journal_text = parsed.get_section_text("journal")
            if journal_text:
                print("\n=== Your journal entry ===")
                print(journal_text)
                print("=" * 30)

        print("\nJournal entry saved!")

    run_with_existing_check(filepath, "Today's journal", create_daily_entry)
