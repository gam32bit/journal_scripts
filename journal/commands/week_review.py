"""Weekly review command."""

from datetime import date
from journal import config, parser, templates, ui, io
from .base import run_with_existing_check
from .writing import scan_writings


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

        # Scan writing output for this week
        date_strs = {d.strftime("%Y-%m-%d") for d in week_dates}
        writings = scan_writings(date_strs)

        if writings:
            reading_reflections = [(t, s, su, st) for t, s, su, st in writings if su and su.strip()]
            other_writings = [(t, s, su, st) for t, s, su, st in writings if not (su and su.strip())]

            if reading_reflections:
                print("\n=== Reading reflections this week ===")
                for title, status, source_url, source_title in reading_reflections:
                    ref = source_title if source_title and source_title.strip() else source_url
                    print(f'  - "{title}" (re: {ref}) ({status})')

            if other_writings:
                print("\n=== Other writing this week ===")
                for title, status, source_url, source_title in other_writings:
                    print(f'  - "{title}" ({status})')

        # Prompt for weekly reflection
        print("\n=== Weekly Reflection ===")
        weekly_reflection = input("How did this week go? ").strip()

        # Prompt for weekly summary bullets
        weekly_summary = ui.get_multi_line_input(
            "\n=== Weekly Summary ===\nWrite 3-5 bullets synthesizing the week:"
        )

        # Build the review content using template
        content = templates.weekly_review_template(
            d=target_date,
            freetime_focuses=freetime_focuses,
            daily_summaries=daily_summaries,
            weekly_reflection=weekly_reflection,
            weekly_summary=weekly_summary,
            writings=writings if writings else None,
        )

        # Write the file
        io.write_file(filepath, content)
        print(f"\nWeekly review saved to: {filepath}")

    run_with_existing_check(filepath, "Weekly review", create_weekly_review)
