"""Monthly planning command."""

from datetime import date
from journal import config, templates, ui, io
from .base import run_with_existing_check


def run(target_date: date = None):
    """Create a monthly plan."""
    if target_date is None:
        target_date = date.today()

    filepath = config.monthly_plan_path(target_date)

    def create_monthly_plan():
        print("=== Monthly Plan Setup ===")
        print("Opening monthly plan template in vim...")
        print("Fill in the sections and save when done.\n")

        # Create the monthly plan template with empty sections
        content = templates.monthly_plan_template(target_date, [], "", [])

        # Write the template file
        io.write_file(filepath, content)

        # Open in vim for editing
        ui.open_in_editor(filepath)

        print(f"\nMonthly plan saved to: {filepath}")

    run_with_existing_check(filepath, "Monthly plan", create_monthly_plan)
