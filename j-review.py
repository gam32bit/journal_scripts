#!/usr/bin/env python3
"""
Weekly Review - Aggregate data from the week into a review document.
Run on Saturdays to reflect on your week.
"""

import sys
from datetime import date
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, parser, writer


def get_multi_line_input(prompt: str) -> list[str]:
    """Get multi-line bullet point input from user."""
    print(f"\n{prompt}")
    print("(Enter bullet points one per line, press Enter on empty line to finish)")

    items = []
    while True:
        line = input("- ").strip()
        if not line:
            break
        items.append(line)

    return items


def main():
    today = date.today()
    filepath = config.review_path(today)

    # Check if already exists
    if filepath.exists():
        action = writer.handle_existing_file(filepath, "Weekly review")
        if action != 'recreate':
            return

    print("=== Weekly Review ===\n")

    # Get week dates
    week_dates = config.get_week_dates(today)
    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    # Find weekly plan
    weekly_path = config.weekly_path(today)
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
    weekly_summary = get_multi_line_input("\n=== Weekly Summary ===\nWrite 3-5 bullets synthesizing the week:")

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
                    writer.open_in_editor(daily_path)

    # Build the review content
    content = f"""# Weekly Review
Week ending: {today.strftime("%B %d, %Y")}

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
    writer.write_file(filepath, content)
    print(f"\nWeekly review saved to: {filepath}")


if __name__ == "__main__":
    main()
