"""Weekly planning command."""

from datetime import date
from journal import config, parser, templates, ui, io
from .base import run_with_existing_check


def run(target_date: date = None):
    """Create a weekly plan."""
    if target_date is None:
        target_date = date.today()

    sunday = config.get_sunday(target_date)
    filepath = config.weekly_path(target_date)

    def create_weekly_plan():
        print("=== Weekly Plan Setup ===")

        # Get freetime focuses from monthly plan
        monthly_path = config.monthly_plan_path(target_date)
        freetime_focuses = []

        if monthly_path.exists():
            parsed = parser.parse_file(monthly_path)
            if parsed:
                freetime_focuses = parsed.get_list_items("freetime")

        # Display freetime focuses from monthly plan
        if freetime_focuses:
            print("Freetime focuses from monthly plan:")
            for focus in freetime_focuses:
                print(f"  - {focus}")
            print()

        print("Opening weekly plan template in vim...")
        print("Fill in the sections and save when done.\n")

        # Create the weekly plan template
        content = f"""# Weekly Plan - {sunday.strftime("%B %d, %Y")}

## Freetime focuses (from monthly plan):
"""
        if freetime_focuses:
            for focus in freetime_focuses:
                content += f"- {focus}\n"
        else:
            content += "- (No freetime focuses in monthly plan)\n"

        content += """
## What's coming up:
-

## How I want to approach this week:


"""

        # Write the template file
        io.write_file(filepath, content)

        # Open in vim for editing
        ui.open_in_editor(filepath)

        print(f"\nWeekly plan saved to: {filepath}")

    run_with_existing_check(filepath, "Weekly plan", create_weekly_plan)
