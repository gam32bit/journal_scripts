"""Weekly planning command."""

from datetime import date
from journal import config, templates, ui, io
from .base import run_with_existing_check


def run(target_date: date = None):
    """Create a weekly plan."""
    if target_date is None:
        target_date = date.today()

    sunday = config.get_sunday(target_date)
    filepath = config.weekly_path(target_date)

    def create_weekly_plan():
        print("=== Weekly Plan Setup ===")
        print("Opening weekly plan template in vim...")
        print("Fill in the sections and save when done.\n")

        # Create the weekly plan template with empty sections
        content = templates.weekly_plan_template(sunday)

        # Write the template file
        io.write_file(filepath, content)

        # Open in vim for editing
        ui.open_in_editor(filepath)

        print(f"\nWeekly plan saved to: {filepath}")

    run_with_existing_check(filepath, "Weekly plan", create_weekly_plan)
