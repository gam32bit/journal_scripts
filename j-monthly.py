#!/usr/bin/env python3
"""
Monthly Review - Aggregate data from weekly reviews into a monthly summary.
Run at the end of each month to reflect on your month.
"""

import sys
from datetime import date, timedelta
from pathlib import Path
from collections import Counter
import calendar

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, parser, writer


def get_month_dates(d: date) -> list[date]:
    """Get all dates in the month containing date d."""
    year, month = d.year, d.month
    num_days = calendar.monthrange(year, month)[1]
    return [date(year, month, day) for day in range(1, num_days + 1)]


def find_weekly_reviews_for_month(d: date) -> list[Path]:
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
                reviews.append(review_file)

    return sorted(reviews)


def find_daily_entries_for_month(d: date) -> list[Path]:
    """Find all daily entry files for the month containing date d."""
    entries = []
    for day in get_month_dates(d):
        daily_file = config.daily_path(day)
        if daily_file.exists():
            entries.append(daily_file)
    return entries


def find_weekly_plans_for_month(d: date) -> list[Path]:
    """Find all weekly plan files for the month containing date d."""
    plans = []
    month_dates = get_month_dates(d)

    # Get unique weeks (by Sunday) that fall in this month
    weeks_seen = set()
    for day in month_dates:
        sunday = config.get_sunday(day)
        if sunday not in weeks_seen:
            weeks_seen.add(sunday)
            weekly_file = config.weekly_path(sunday)
            if weekly_file.exists():
                plans.append(weekly_file)

    return sorted(plans)


def calculate_sleep_data(d: date) -> dict:
    """Calculate sleep statistics for the month."""
    daily_entries = find_daily_entries_for_month(d)

    sleep_hours = []
    for entry in daily_entries:
        parsed = parser.parse_file(entry)
        if parsed:
            hours_str = parsed.get_sleep_hours()
            if hours_str:
                try:
                    sleep_hours.append(float(hours_str))
                except ValueError:
                    pass

    if not sleep_hours:
        return {
            "average": 0.0,
            "trend": 0.0,
            "daily_values": []
        }

    avg = sum(sleep_hours) / len(sleep_hours)

    # Get previous month's average for trend
    prev_month_date = d.replace(day=1) - timedelta(days=1)
    prev_entries = find_daily_entries_for_month(prev_month_date)
    prev_sleep_hours = []

    for entry in prev_entries:
        parsed = parser.parse_file(entry)
        if parsed:
            hours_str = parsed.get_sleep_hours()
            if hours_str:
                try:
                    prev_sleep_hours.append(float(hours_str))
                except ValueError:
                    pass

    prev_avg = sum(prev_sleep_hours) / len(prev_sleep_hours) if prev_sleep_hours else 0.0
    trend = avg - prev_avg if prev_avg > 0 else 0.0

    return {
        "average": avg,
        "trend": trend,
        "daily_values": sleep_hours
    }


def aggregate_tags(d: date) -> dict:
    """Aggregate tag data for the month."""
    daily_entries = find_daily_entries_for_month(d)

    tag_counter = Counter()
    for entry in daily_entries:
        parsed = parser.parse_file(entry)
        if parsed:
            tags = parsed.get_tags()
            tag_counter.update(tags)

    # Get previous month's tags for comparison
    prev_month_date = d.replace(day=1) - timedelta(days=1)
    prev_entries = find_daily_entries_for_month(prev_month_date)
    prev_tag_counter = Counter()

    for entry in prev_entries:
        parsed = parser.parse_file(entry)
        if parsed:
            tags = parsed.get_tags()
            prev_tag_counter.update(tags)

    # Find new and dropped tags
    current_tags = set(tag_counter.keys())
    prev_tags = set(prev_tag_counter.keys())

    new_tags = current_tags - prev_tags
    dropped_tags = prev_tags - current_tags

    return {
        "tag_counter": tag_counter,
        "new_tags": sorted(new_tags),
        "dropped_tags": sorted(dropped_tags)
    }


def collect_focus_areas(d: date) -> list[str]:
    """Collect all focus areas from weekly plans in the month."""
    weekly_plans = find_weekly_plans_for_month(d)

    focus_areas = []
    for plan in weekly_plans:
        parsed = parser.parse_file(plan)
        if parsed:
            areas = parsed.get_list_items("focus")
            focus_areas.extend(areas)

    return focus_areas


def collect_eating_intentions(d: date) -> list[str]:
    """Collect eating intentions from weekly plans in the month."""
    weekly_plans = find_weekly_plans_for_month(d)

    intentions = []
    for plan in weekly_plans:
        parsed = parser.parse_file(plan)
        if parsed:
            intention = parsed.get_section_text("eating_intention")
            if intention:
                intentions.append(intention)

    return intentions


def calculate_consistency(d: date) -> dict:
    """Calculate consistency metrics for the month."""
    daily_count = len(find_daily_entries_for_month(d))
    weekly_plan_count = len(find_weekly_plans_for_month(d))
    weekly_review_count = len(find_weekly_reviews_for_month(d))

    return {
        "daily_entries": daily_count,
        "weekly_plans": weekly_plan_count,
        "weekly_reviews": weekly_review_count
    }


def print_summary_tables(d: date):
    """Print summary tables to terminal."""
    month_name = d.strftime("%B %Y")

    print(f"\n=== Monthly Review for {month_name} ===\n")

    # Consistency
    consistency = calculate_consistency(d)
    print("=== Consistency ===")
    print(f"Daily entries: {consistency['daily_entries']}")
    print(f"Weekly plans: {consistency['weekly_plans']}")
    print(f"Weekly reviews: {consistency['weekly_reviews']}")

    # Sleep
    sleep_data = calculate_sleep_data(d)
    print("\n=== Sleep ===")
    print(f"Monthly average: {sleep_data['average']:.1f} hours")
    if sleep_data['trend'] != 0.0:
        trend_sign = "+" if sleep_data['trend'] > 0 else ""
        print(f"Trend: {trend_sign}{sleep_data['trend']:.1f} vs previous month")
    else:
        print("Trend: No previous month data")

    # Tags
    tag_data = aggregate_tags(d)
    print("\n=== Emotional Landscape ===")
    print("Top 10 tags:")
    for tag, count in tag_data['tag_counter'].most_common(10):
        print(f"  {tag}: {count}")

    if tag_data['new_tags']:
        print("\nNew this month:")
        for tag in tag_data['new_tags']:
            print(f"  - {tag}")

    if tag_data['dropped_tags']:
        print("\nDropped off:")
        for tag in tag_data['dropped_tags']:
            print(f"  - {tag}")

    # Focus areas
    focus_areas = collect_focus_areas(d)
    print("\n=== Focus Areas This Month ===")
    if focus_areas:
        # Get unique focus areas while preserving order
        unique_areas = []
        seen = set()
        for area in focus_areas:
            if area not in seen:
                unique_areas.append(area)
                seen.add(area)

        for area in unique_areas:
            print(f"  - {area}")
    else:
        print("  No focus areas defined")

    # Eating intentions
    intentions = collect_eating_intentions(d)
    print("\n=== Eating Intentions This Month ===")
    if intentions:
        for i, intention in enumerate(intentions, 1):
            print(f"  Week {i}: {intention}")
    else:
        print("  No eating intentions recorded")

    return {
        "consistency": consistency,
        "sleep": sleep_data,
        "tags": tag_data,
        "focus_areas": focus_areas,
        "intentions": intentions
    }


def generate_monthly_review_content(d: date, data: dict, reflection: str, one_word: str) -> str:
    """Generate the monthly review markdown content."""
    month_name = d.strftime("%B %Y")

    content = f"""# Monthly Review
Month: {month_name}

## Consistency
- Daily entries: {data['consistency']['daily_entries']}
- Weekly plans: {data['consistency']['weekly_plans']}
- Weekly reviews: {data['consistency']['weekly_reviews']}

## Sleep
- Monthly average: {data['sleep']['average']:.1f} hours
"""

    if data['sleep']['trend'] != 0.0:
        trend_sign = "+" if data['sleep']['trend'] > 0 else ""
        content += f"- Trend: {trend_sign}{data['sleep']['trend']:.1f} vs previous month\n"
    else:
        content += "- Trend: No previous month data\n"

    content += "\n## Emotional Landscape\n### Top tags:\n"
    for tag, count in data['tags']['tag_counter'].most_common(10):
        content += f"- {tag}: {count}\n"

    if data['tags']['new_tags']:
        content += "\n### New this month:\n"
        for tag in data['tags']['new_tags']:
            content += f"- {tag}\n"

    if data['tags']['dropped_tags']:
        content += "\n### Dropped off:\n"
        for tag in data['tags']['dropped_tags']:
            content += f"- {tag}\n"

    content += "\n## Focus Areas This Month\n"
    if data['focus_areas']:
        # Get unique focus areas
        unique_areas = []
        seen = set()
        for area in data['focus_areas']:
            if area not in seen:
                unique_areas.append(area)
                seen.add(area)

        for area in unique_areas:
            content += f"- {area}\n"
    else:
        content += "No focus areas defined\n"

    content += "\n## Eating Intentions This Month\n"
    if data['intentions']:
        for i, intention in enumerate(data['intentions'], 1):
            content += f"- Week {i}: {intention}\n"
    else:
        content += "No eating intentions recorded\n"

    content += f"""
---

## Monthly Reflection

Month in one word: {one_word}

Narrative summary:
{reflection}
"""

    return content


def main():
    today = date.today()
    filepath = config.monthly_path(today)

    # Check if already exists
    if filepath.exists():
        action = writer.handle_existing_file(filepath, "Monthly review")
        if action != 'recreate':
            return

    # Print summary tables and collect data
    data = print_summary_tables(today)

    # Prompt for reflection
    print("\n--- Monthly Reflection ---")
    one_word = input("Month in one word: ").strip()
    print("Write a brief narrative summary of this month (2-3 sentences):")
    print("(Press Ctrl+D or Ctrl+Z when finished)")

    narrative_lines = []
    try:
        while True:
            line = input()
            narrative_lines.append(line)
    except EOFError:
        pass

    narrative = "\n".join(narrative_lines).strip()

    # Generate and save content
    content = generate_monthly_review_content(today, data, narrative, one_word)
    writer.write_file(filepath, content)
    print(f"\nMonthly review saved to: {filepath}")


if __name__ == "__main__":
    main()
