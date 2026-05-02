"""Monthly review command."""

import calendar
from datetime import date, timedelta
from journal import config, parser, templates, ui, io
from .base import run_with_existing_check


def get_month_dates(d: date) -> list[date]:
    """Get all dates in the month containing date d."""
    year, month = d.year, d.month
    num_days = calendar.monthrange(year, month)[1]
    return [date(year, month, day) for day in range(1, num_days + 1)]


def find_weekly_reviews_for_month(d: date) -> list[tuple[date, any]]:
    """Find all weekly review files for the month containing date d."""
    reviews = []
    month_dates = get_month_dates(d)

    # Get unique weeks (by Sunday) that fall in this month
    weeks_seen = set()
    for day in month_dates:
        sunday = config.get_sunday(day)
        if sunday not in weeks_seen:
            weeks_seen.add(sunday)
            # Review is on Saturday of that week
            saturday = sunday + timedelta(days=6)
            review_file = config.review_path(saturday)
            if review_file.exists():
                reviews.append((sunday, review_file))

    return sorted(reviews, key=lambda x: x[0])


def find_daily_entries_for_month(d: date) -> list[any]:
    """Find all daily entry files for the month containing date d."""
    entries = []
    for day in get_month_dates(d):
        daily_file = config.daily_path(day)
        if daily_file.exists():
            entries.append(daily_file)
    return entries


def collect_weekly_reflections(d: date) -> list[tuple[date, str]]:
    """Collect 'how did this week go' reflections from each weekly review in the month."""
    weekly_reviews = find_weekly_reviews_for_month(d)

    reflections = []
    for sunday, review_file in weekly_reviews:
        parsed = parser.parse_file(review_file)
        if parsed:
            reflection = parsed.get_section_text("weekly_reflection")
            if reflection:
                reflections.append((sunday, reflection))

    return reflections


def calculate_consistency(d: date) -> dict:
    """Calculate consistency metrics for the month."""
    daily_count = len(find_daily_entries_for_month(d))
    weekly_review_count = len(find_weekly_reviews_for_month(d))

    return {
        "daily_entries": daily_count,
        "weekly_reviews": weekly_review_count,
    }


def run(target_date: date = None):
    """Create a monthly review."""
    if target_date is None:
        target_date = date.today()

    filepath = config.monthly_path(target_date)

    def create_monthly_review():
        month_name = target_date.strftime("%B %Y")

        print(f"\n=== Monthly Review for {month_name} ===\n")

        # Consistency
        consistency = calculate_consistency(target_date)
        print("=== Consistency ===")
        print(f"Daily entries: {consistency['daily_entries']}")
        print(f"Weekly reviews: {consistency['weekly_reviews']}")

        # Weekly reflections grouped by week
        print("\n=== Weekly reflections ===")
        weekly_reflections = collect_weekly_reflections(target_date)
        if weekly_reflections:
            for sunday, reflection in weekly_reflections:
                print(f"\nWeek ending {(sunday + timedelta(days=6)).strftime('%B %d')}:")
                print(f"  {reflection}")
        else:
            print("  (No weekly reflections found)")

        # Weekly summaries
        print("\n=== Weekly summaries ===")
        weekly_reviews = find_weekly_reviews_for_month(target_date)
        weekly_review_summaries = []

        for sunday, review in weekly_reviews:
            parsed = parser.parse_file(review)
            if parsed:
                summary = parsed.get_list_items("weekly_summary")
                if summary:
                    weekly_review_summaries.append((sunday, summary))
                    print(f"\nWeek ending {(sunday + timedelta(days=6)).strftime('%B %d')}:")
                    for bullet in summary:
                        print(f"  - {bullet}")

        if not weekly_review_summaries:
            print("  (No weekly summaries found)")

        # Offer to open specific weekly reviews
        if weekly_reviews:
            print(f"\n--- Weekly Reviews ---")
            print(f"Found {len(weekly_reviews)} weekly reviews")
            choice = input("Enter week number to open review (1-N), or press Enter to continue: ").strip()

            if choice.isdigit():
                week_index = int(choice) - 1
                if 0 <= week_index < len(weekly_reviews):
                    _, review_path = weekly_reviews[week_index]
                    print(f"Opening weekly review...")
                    ui.open_in_editor(review_path)

        # Prompt for monthly summary
        monthly_summary = ui.get_multi_line_input("\n=== Monthly Summary ===\nWrite bullets synthesizing the month:")

        # Prompt for monthly reflection
        print("\n=== Monthly Reflection ===")
        monthly_reflection = input("How did this month go? ").strip()

        # Build the monthly review content using template
        content = templates.monthly_review_template(
            d=target_date,
            consistency=consistency,
            weekly_reflections=weekly_reflections,
            weekly_summaries=weekly_review_summaries,
            monthly_summary=monthly_summary,
            monthly_reflection=monthly_reflection,
        )

        # Write the file
        io.write_file(filepath, content)
        print(f"\nMonthly review saved to: {filepath}")

    run_with_existing_check(filepath, "Monthly review", create_monthly_review)
