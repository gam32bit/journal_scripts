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
        print("=== Weekly Plan Setup ===\n")

        # What's coming up this week?
        coming_up = ui.get_multi_line_input("What's coming up this week?")

        # How do you want to approach this week?
        approach = ui.get_multi_line_text("\nHow do you want to approach this week?")

        # Freetime focuses
        freetime = ui.get_multi_line_input("\nWhat are your freetime focuses for this week?")

        # Eating intention
        print("\n--- Eating Intention ---")
        eating_intention = input("Enter your eating intention for this week: ").strip()

        # Create the weekly plan content
        content = templates.weekly_plan_template(sunday, coming_up, approach, freetime, eating_intention)

        # Write the file
        io.write_file(filepath, content)
        print(f"\nWeekly plan saved to: {filepath}")

    run_with_existing_check(filepath, "Weekly plan", create_weekly_plan)
