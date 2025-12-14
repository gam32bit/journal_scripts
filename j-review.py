#!/usr/bin/env python3
"""
Weekly Review - Aggregate data from the week into a review document.
Run on Saturdays to reflect on your week.
"""

import sys
from datetime import date
from pathlib import Path
from collections import Counter

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, parser, templates, writer


def calculate_sleep_average(scores: list[str | None]) -> float | None:
    """Calculate average sleep score from X/-/O values."""
    score_map = {"O": 1.0, "-": 0.5, "X": 0.0}
    values = [score_map[s] for s in scores if s in score_map]
    if not values:
        return None
    return sum(values) / len(values)


def main():
    today = date.today()
    filepath = config.review_path(today)
    
    # Check if already exists
    if filepath.exists():
        print(f"Weekly review already exists: {filepath}")
        print("Opening existing file...")
        writer.open_in_editor(filepath)
        return
    
    print(f"Generating weekly review...")
    
    # Get week dates
    week_dates = config.get_week_dates(today)
    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    
    # Find files
    daily_files = parser.find_daily_files(today)
    prompt_files = parser.find_prompt_files(today)
    weekly_path = config.weekly_path(today)
    
    print(f"  Found {len(daily_files)} daily entries")
    print(f"  Found {len(prompt_files)} writing entries")
    
    # Aggregate sleep data
    sleep_scores = []  # (day_name, score)
    all_scores = []
    
    for i, d in enumerate(week_dates):
        daily_path = config.daily_path(d)
        parsed = parser.parse_file(daily_path)
        score = parsed.get_sleep_score() if parsed else None
        sleep_scores.append((day_names[i], score))
        if score:
            all_scores.append(score)
    
    sleep_avg = calculate_sleep_average(all_scores)
    
    # Aggregate tags
    tag_counter = Counter()
    tag_timeline = {}  # tag -> [day_names]
    
    for i, d in enumerate(week_dates):
        daily_path = config.daily_path(d)
        parsed = parser.parse_file(daily_path)
        if parsed:
            tags = parsed.get_tags()
            tag_counter.update(tags)
            for tag in tags:
                if tag not in tag_timeline:
                    tag_timeline[tag] = []
                tag_timeline[tag].append(day_names[i])
    
    tag_frequency = tag_counter.most_common()
    
    # Aggregate eating reflections
    eating_reflections = []
    
    for d in week_dates:
        daily_path = config.daily_path(d)
        parsed = parser.parse_file(daily_path)
        if parsed:
            text = parsed.get_section_text("eating")
            if text:
                eating_reflections.append((d.strftime("%Y-%m-%d"), text))
    
    # Aggregate writing excerpts
    writing_excerpts = []
    
    for d in week_dates:
        prompt_path = config.prompt_path(d)
        parsed = parser.parse_file(prompt_path)
        if parsed:
            prompt = parsed.get_section_text("todays_prompt")
            writing = parsed.get_section_text("writing")
            if prompt or writing:
                # Get first 3 lines of writing as excerpt
                excerpt = "\n".join(writing.split("\n")[:3]) if writing else ""
                writing_excerpts.append((d.strftime("%Y-%m-%d"), prompt, excerpt))
    
    # Get task status from weekly plan
    completed_tasks = []
    incomplete_tasks = []
    focus_areas = []
    
    if weekly_path.exists():
        parsed = parser.parse_file(weekly_path)
        if parsed:
            # Get completed from completed section
            for line in parsed.get_section("completed"):
                stripped = line.strip()
                if stripped:
                    completed_tasks.append(stripped)
            
            # Get checked tasks too
            checked, unchecked = parsed.get_checked_items("tasks")
            for task in checked:
                if task not in completed_tasks:
                    completed_tasks.append(task)
            
            incomplete_tasks = unchecked
            focus_areas = parsed.get_list_items("focus")
    
    # Generate review
    content = templates.weekly_review_template(
        today,
        len(daily_files),
        len(prompt_files),
        sleep_avg,
        sleep_scores,
        eating_reflections,
        tag_frequency,
        tag_timeline,
        writing_excerpts,
        completed_tasks,
        incomplete_tasks,
        focus_areas,
    )
    
    writer.write_file(filepath, content)
    
    print("Opening in editor...")
    writer.open_in_editor(filepath)
    
    print("Weekly review complete!")


if __name__ == "__main__":
    main()
