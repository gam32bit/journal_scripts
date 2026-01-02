"""Weekly review command."""

from datetime import date
from journal import config, parser, ui, io
from .base import run_with_existing_check


def run(target_date: date = None):
    """Create a weekly review."""
    if target_date is None:
        target_date = date.today()

    filepath = config.review_path(target_date)

    def create_weekly_review():
        print("=== Weekly Review ===\n")

        # Get week dates
        week_dates = config.get_week_dates(target_date)
        day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        # Find weekly plan
        weekly_path = config.weekly_path(target_date)
        coming_up = []
        freetime_focuses = []

        if weekly_path.exists():
            parsed = parser.parse_file(weekly_path)
            if parsed:
                coming_up = parsed.get_list_items("coming_up")
                freetime_focuses = parsed.get_list_items("freetime")

        # Display what was coming up this week
        print("=== What came up this week ===")
        if coming_up:
            for item in coming_up:
                print(f"  - {item}")
        else:
            print("  (No items listed in weekly plan)")

        # Collect and display daily summaries
        print("\n=== Daily Summaries ===")
        daily_summaries = {}
        daily_files = []

        for i, d in enumerate(week_dates):
            daily_path = config.daily_path(d)
            if daily_path.exists():
                daily_files.append(daily_path)
                parsed = parser.parse_file(daily_path)
                if parsed:
                    summaries = parsed.get_summary_bullets()
                    if summaries:
                        daily_summaries[day_names[i]] = summaries
                        print(f"\n{day_names[i]}:")
                        for bullet in summaries:
                            print(f"  - {bullet}")

        if not daily_summaries:
            print("  (No daily summaries found)")

        # Calculate health metrics
        print("\n=== Health this week ===")

        # Sleep average
        sleep_hours = []
        mindful_eating_count = 0

        for d in week_dates:
            daily_path = config.daily_path(d)
            if daily_path.exists():
                parsed = parser.parse_file(daily_path)
                if parsed:
                    # Sleep
                    hours_str = parsed.get_sleep_hours()
                    if hours_str:
                        try:
                            sleep_hours.append(float(hours_str))
                        except ValueError:
                            pass

                    # Mindful eating
                    mindful = parsed.get_mindful_eating()
                    if mindful and mindful.strip():
                        mindful_eating_count += 1

        sleep_avg = sum(sleep_hours) / len(sleep_hours) if sleep_hours else 0.0
        print(f"Sleep average: {sleep_avg:.1f} hours")
        print(f"Days with mindful eating logged: {mindful_eating_count}/7")

        # Display freetime focuses
        print("\n=== Freetime focuses ===")
        if freetime_focuses:
            for focus in freetime_focuses:
                print(f"  - {focus}")
        else:
            print("  (No freetime focuses defined)")

        # Ask about freetime focuses
        print("\n--- Reflection on Freetime Focuses ---")
        freetime_reflection = input("How did these go? ").strip()

        # Prompt for weekly summary bullets
        weekly_summary = ui.get_multi_line_input("\n=== Weekly Summary ===\nWrite 3-5 bullets synthesizing the week:")

        # Offer to open a specific daily entry
        if daily_files:
            print(f"\n--- Daily Entries ---")
            print(f"Found {len(daily_files)} daily entries")
            choice = input("Enter day number to open (1=Sun, 2=Mon, ..., 7=Sat), or press Enter to continue: ").strip()

            if choice.isdigit():
                day_index = int(choice) - 1
                if 0 <= day_index < 7:
                    daily_path = config.daily_path(week_dates[day_index])
                    if daily_path.exists():
                        print(f"Opening {day_names[day_index]}'s entry...")
                        ui.open_in_editor(daily_path)

        # Build the review content
        content = f"""# Weekly Review
Week ending: {target_date.strftime("%B %d, %Y")}

## What came up this week:
"""
        if coming_up:
            for item in coming_up:
                content += f"- {item}\n"
        else:
            content += "(No items listed in weekly plan)\n"

        content += "\n## Daily summaries:\n"
        for day_name, summaries in daily_summaries.items():
            content += f"\n### {day_name}\n"
            for bullet in summaries:
                content += f"- {bullet}\n"

        content += f"\n## Freetime focuses:\n"
        if freetime_focuses:
            for focus in freetime_focuses:
                content += f"- {focus}\n"
        else:
            content += "(No freetime focuses defined)\n"

        content += f"\nReflection: {freetime_reflection}\n"

        content += f"\n## Health this week:\n"
        content += f"- Sleep average: {sleep_avg:.1f} hours\n"
        content += f"- Days with mindful eating logged: {mindful_eating_count}/7\n"

        content += "\n## Weekly summary:\n"
        for bullet in weekly_summary:
            content += f"- {bullet}\n"

        # Write the file
        io.write_file(filepath, content)
        print(f"\nWeekly review saved to: {filepath}")

    run_with_existing_check(filepath, "Weekly review", create_weekly_review)
