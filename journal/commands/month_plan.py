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
        month_name = target_date.strftime("%B %Y")
        print(f"=== Monthly Plan: {month_name} ===\n")

        coming_up = ui.get_multi_line_input("What's coming up this month? (events, deadlines, trips)")

        print()
        themes = input("Themes or intentions for the month: ").strip()

        freetime = ui.get_multi_line_input("\nFreetime focuses to prioritize:")

        content = templates.monthly_plan_template(target_date, coming_up, themes, freetime)
        io.write_file(filepath, content)
        print(f"\nMonthly plan saved to: {filepath}")

    run_with_existing_check(filepath, "Monthly plan", create_monthly_plan)
