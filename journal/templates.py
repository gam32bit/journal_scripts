"""
Templates for journal files.
Generates content for new entries.
"""

from datetime import date


def weekly_plan_template(d: date) -> str:
    """Generate weekly plan template."""
    return f"""# Weekly Plan
Week of: {d.strftime("%B %d, %Y")}

## Focus areas:
-
-

"""


def daily_journal_template(
    d: date,
    focus_areas: list[str],
    weekly_file: str | None = None,
) -> str:
    """Generate daily journal template."""

    # Format focus areas
    if focus_areas:
        focus_str = "\n".join(f"- {area}" for area in focus_areas)
    else:
        focus_str = "(No focus areas defined)"

    weekly_ref = f"\n[weekly_file:{weekly_file}]" if weekly_file else ""

    return f"""# Daily Journal
Date: {d.strftime("%A, %B %d, %Y")}

## Focus areas:
{focus_str}

---

## Sleep quality:

## Yesterday's eating reflection:


## Journal entry:


## Tags:
{weekly_ref}
"""


def weekly_review_template(
    d: date,
    daily_count: int,
    sleep_avg: float | None,
    sleep_scores: list[tuple[str, str | None]],  # (day_name, score)
    eating_reflections: list[tuple[str, str]],   # (date_str, text)
    tag_frequency: list[tuple[str, int]],        # (tag, count)
    tag_timeline: dict[str, list[str]],          # tag -> [day_names]
    focus_areas: list[str],
) -> str:
    """Generate weekly review template."""
    
    # Sleep section
    if sleep_avg is not None:
        sleep_avg_str = f"{sleep_avg:.2f}"
    else:
        sleep_avg_str = "N/A"
    
    sleep_detail = []
    for day_name, score in sleep_scores:
        score_str = score if score else "-"
        sleep_detail.append(f"  {day_name}: {score_str}")
    sleep_detail_str = "\n".join(sleep_detail) if sleep_detail else "  (No data)"
    
    # Tag frequency
    if tag_frequency:
        max_count = max(count for _, count in tag_frequency)
        tag_freq_lines = []
        for tag, count in tag_frequency[:10]:  # Top 10
            bar = "█" * int((count / max_count) * 20)
            tag_freq_lines.append(f"  {tag}: {bar} ({count})")
        tag_freq_str = "\n".join(tag_freq_lines)
    else:
        tag_freq_str = "  (No tags recorded)"
    
    # Tag timeline
    if tag_timeline:
        timeline_lines = [f"  {tag}: {', '.join(days)}" for tag, days in sorted(tag_timeline.items())]
        tag_timeline_str = "\n".join(timeline_lines)
    else:
        tag_timeline_str = "  (No tags recorded)"
    
    # Eating reflections
    if eating_reflections:
        eating_lines = []
        for date_str, text in eating_reflections:
            eating_lines.append(f"[{date_str}]")
            eating_lines.append(text)
            eating_lines.append("")
        eating_str = "\n".join(eating_lines)
    else:
        eating_str = "(No eating reflections recorded)"

    # Focus areas
    if focus_areas:
        focus_str = "\n".join(f"- {area}" for area in focus_areas)
    else:
        focus_str = "(No focus areas defined)"
    
    return f"""# Weekly Review
Week ending: {d.strftime("%B %d, %Y")}

Daily entries found: {daily_count}

## Sleep analysis:
Average: {sleep_avg_str} (O=1.0, -=0.5, X=0.0)

{sleep_detail_str}

## Emotional landscape (Tags):

Frequency:
{tag_freq_str}

Timeline:
{tag_timeline_str}

## Eating reflections:
{eating_str}

## Focus areas this week:
{focus_str}

---

## Weekly reflection:

How did you do with your focus areas this week?


What went well this week?


What could be improved?


Key insights or lessons learned:


"""
