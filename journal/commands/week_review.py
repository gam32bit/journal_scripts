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

        # Get week dates
        week_dates = config.get_week_dates(target_date)
        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        # Find weekly plan
        weekly_path = config.weekly_path(target_date)
        freetime_focuses = []
        approach_text = ""

        if weekly_path.exists():
            parsed = parser.parse_file(weekly_path)
            if parsed:
                freetime_focuses = parsed.get_list_items("freetime")
                approach_text = parsed.get_section_text("approach")

        # Collect sleep hours and mindful eating logs
        sleep_data = []  # List of (day_name, hours) tuples
        mindful_eating_logs = []  # List of (day_name, log_text) tuples

        for i, d in enumerate(week_dates):
            daily_path = config.daily_path(d)
            if daily_path.exists():
                parsed = parser.parse_file(daily_path)
                if parsed:
                    # Sleep
                    hours_str = parsed.get_sleep_hours()
                    if hours_str:
                        try:
                            hours = float(hours_str)
                            sleep_data.append((day_names[i], hours))
                        except ValueError:
                            pass

                    # Mindful eating
                    mindful = parsed.get_mindful_eating()
                    if mindful and mindful.strip():
                        mindful_eating_logs.append((day_names[i], mindful))

        # Display sleep with ASCII bars
        print("=== Sleep this week ===")
        if sleep_data:
            sleep_avg = sum(h for _, h in sleep_data) / len(sleep_data)
            print(f"Average: {sleep_avg:.1f} hours\n")

            for day_name, hours in sleep_data:
                # Create ASCII bar (each █ represents 1 hour)
                full_blocks = int(hours)
                partial = hours - full_blocks
                bar = "█" * full_blocks
                if partial >= 0.5:
                    bar += "▌"
                print(f"{day_name}: {bar} {hours:.1f}h")
        else:
            print("  (No sleep data found)")

        # Display mindful eating logs
        print("\n=== Mindful eating logs ===")
        if mindful_eating_logs:
            for day_name, log in mindful_eating_logs:
                print(f"{day_name}: {log}")
        else:
            print("  (No mindful eating logs found)")

        # Display freetime focuses
        print("\n=== Freetime focuses ===")
        if freetime_focuses:
            for focus in freetime_focuses:
                print(f"  - {focus}")
        else:
            print("  (No freetime focuses defined)")

        # Display approach for this week
        print("\n=== Approach for this week ===")
        if approach_text:
            print(approach_text)
        else:
            print("  (No approach defined)")

        # Collect daily summaries
        print("\n=== Daily Summaries ===")
        daily_summaries = {}

        for i, d in enumerate(week_dates):
            daily_path = config.daily_path(d)
            if daily_path.exists():
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

        # Prompt for weekly reflection
        print("\n=== Weekly Reflection ===")
        weekly_reflection = input("How did this week go? ").strip()

        # Prompt for weekly summary bullets
        weekly_summary = ui.get_multi_line_input("\n=== Weekly Summary ===\nWrite 3-5 bullets synthesizing the week:")

        # Build the review content using template
        content = templates.weekly_review_template(
            d=target_date,
            sleep_data=sleep_data,
            mindful_eating_logs=mindful_eating_logs,
            freetime_focuses=freetime_focuses,
            daily_summaries=daily_summaries,
            weekly_reflection=weekly_reflection,
            weekly_summary=weekly_summary,
        )

        # Write the file
        io.write_file(filepath, content)
        print(f"\nWeekly review saved to: {filepath}")

    run_with_existing_check(filepath, "Weekly review", create_weekly_review)
