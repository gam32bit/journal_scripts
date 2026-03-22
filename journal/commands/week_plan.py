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
        print(f"=== Weekly Plan: {sunday.strftime('%B %d, %Y')} ===\n")

        # Get freetime focuses from monthly plan
        monthly_path = config.monthly_plan_path(target_date)
        monthly_freetime = []

        if monthly_path.exists():
            parsed = parser.parse_file(monthly_path)
            if parsed:
                monthly_freetime = parsed.get_list_items("freetime")

        # Display freetime focuses from monthly plan for reference
        if monthly_freetime:
            print("Freetime focuses from monthly plan:")
            for focus in monthly_freetime:
                print(f"  - {focus}")
            print()

        coming_up = ui.get_multi_line_input("\nWhat's coming up this week?")
        
        freetime_focuses = ui.get_multi_line_input("Freetime focuses this week:")

        print()
        approach = input("How do you want to approach this week? ").strip()

        writing_ideas = ui.get_multi_line_input("\nWriting ideas for this week:")

        # Build content
        content = f"# Weekly Plan - {sunday.strftime('%B %d, %Y')}\n"

        if monthly_freetime:
            content += "\n## Freetime focuses (from monthly plan):\n"
            for focus in monthly_freetime:
                content += f"- {focus}\n"

        content += "\n## Freetime focuses this week:\n"
        if freetime_focuses:
            for focus in freetime_focuses:
                content += f"- {focus}\n"
        else:
            content += "-\n"

        content += "\n## What's coming up:\n"
        if coming_up:
            for item in coming_up:
                content += f"- {item}\n"
        else:
            content += "-\n"

        content += "\n## How I want to approach this week:\n"
        if approach:
            content += f"{approach}\n"

        content += "\n## Writing ideas:\n"
        if writing_ideas:
            for idea in writing_ideas:
                content += f"- {idea}\n"
        else:
            content += "-\n"

        content += "\n"

        io.write_file(filepath, content)
        print(f"\nWeekly plan saved to: {filepath}")

    run_with_existing_check(filepath, "Weekly plan", create_weekly_plan)
