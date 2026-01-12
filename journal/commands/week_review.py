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
        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        # Find weekly plan
        weekly_path = config.weekly_path(target_date)
        freetime_focuses = []

        if weekly_path.exists():
            parsed = parser.parse_file(weekly_path)
            if parsed:
                freetime_focuses = parsed.get_list_items("freetime")

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

        # Ask about freetime focuses
        print()
        freetime_reflection = input("How did these go? ").strip()

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

        # Prompt for weekly summary bullets
        weekly_summary = ui.get_multi_line_input("\n=== Weekly Summary ===\nWrite 3-5 bullets synthesizing the week:")

        # Build the review content
        content = f"""# Weekly Review - {target_date.strftime("%B %d, %Y")}

## Sleep this week:
"""
        if sleep_data:
            sleep_avg = sum(h for _, h in sleep_data) / len(sleep_data)
            content += f"Average: {sleep_avg:.1f} hours\n\n"
            for day_name, hours in sleep_data:
                full_blocks = int(hours)
                partial = hours - full_blocks
                bar = "█" * full_blocks
                if partial >= 0.5:
                    bar += "▌"
                content += f"{day_name}: {bar} {hours:.1f}h\n"
        else:
            content += "(No sleep data found)\n"

        content += "\n## Mindful eating logs:\n"
        if mindful_eating_logs:
            for day_name, log in mindful_eating_logs:
                content += f"{day_name}: {log}\n"
        else:
            content += "(No mindful eating logs found)\n"

        content += "\n## Freetime focuses:\n"
        if freetime_focuses:
            for focus in freetime_focuses:
                content += f"- {focus}\n"
        else:
            content += "(No freetime focuses defined)\n"

        content += f"\nReflection: {freetime_reflection}\n"

        content += "\n## Daily summaries:\n"
        if daily_summaries:
            for day_name, summaries in daily_summaries.items():
                content += f"\n### {day_name}\n"
                for bullet in summaries:
                    content += f"- {bullet}\n"
        else:
            content += "(No daily summaries found)\n"

        content += "\n## Weekly summary:\n"
        for bullet in weekly_summary:
            content += f"- {bullet}\n"

        # Write the file
        io.write_file(filepath, content)
        print(f"\nWeekly review saved to: {filepath}")

    run_with_existing_check(filepath, "Weekly review", create_weekly_review)
