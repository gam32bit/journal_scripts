"""
Templates for journal files.
Generates content for new entries.
"""

from datetime import date, timedelta


def weekly_plan_template(d: date) -> str:
    """Generate weekly plan template."""
    return f"""# Weekly Plan - {d.strftime("%B %d, %Y")}

## What's coming up:
-

## How I want to approach this week:


## Freetime focuses:
-

"""


def daily_journal_template(
    d: date,
    sleep_hours: str,
    freetime_focuses: list[str],
) -> str:
    """Generate daily journal template."""

    # Format freetime focuses
    if freetime_focuses:
        freetime_str = "\n".join(f"- {focus}" for focus in freetime_focuses)
    else:
        freetime_str = "(No freetime focuses defined)"

    return f"""---
sleep_hours: {sleep_hours}
mindful_eating:
---

# Daily Entry - {d.strftime("%A, %B %d, %Y")}

## Freetime focuses:
{freetime_str}

---

## Journal entry:

"""


def monthly_plan_template(d: date, coming_up: list[str], themes: str, freetime: list[str]) -> str:
    """Generate monthly plan template."""
    coming_up_str = "\n".join(f"- {item}" for item in coming_up) if coming_up else "- "
    freetime_str = "\n".join(f"- {item}" for item in freetime) if freetime else "- "

    return f"""# Monthly Plan
Month: {d.strftime("%B %Y")}

## What's coming up this month:
{coming_up_str}

## Themes or intentions:
{themes if themes else ""}

## Freetime focuses to prioritize:
{freetime_str}
"""


def weekly_review_template(
    d: date,
    sleep_data: list[tuple[str, float]],
    mindful_eating_logs: list[tuple[str, str]],
    freetime_focuses: list[str],
    daily_summaries: dict[str, list[str]],
    weekly_reflection: str,
    weekly_summary: list[str],
) -> str:
    """Generate weekly review content."""
    content = f"""# Weekly Review - {d.strftime("%B %d, %Y")}

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

    content += "\n## Daily summaries:\n"
    if daily_summaries:
        for day_name, summaries in daily_summaries.items():
            content += f"\n### {day_name}\n"
            for bullet in summaries:
                content += f"- {bullet}\n"
    else:
        content += "(No daily summaries found)\n"

    content += "\n## Weekly reflection:\n"
    if weekly_reflection:
        content += f"{weekly_reflection}\n"

    content += "\n## Weekly summary:\n"
    for bullet in weekly_summary:
        content += f"- {bullet}\n"

    return content


def monthly_review_template(
    d: date,
    consistency: dict,
    freetime_focuses: list[str],
    sleep_data: dict,
    mindful_eating_days: int,
    weekly_summaries: list[tuple[date, list[str]]],
    monthly_summary: list[str],
    monthly_reflection: str,
) -> str:
    """Generate monthly review content."""
    month_name = d.strftime("%B %Y")

    content = f"""# Monthly Review
Month: {month_name}

## Consistency:
- Daily entries: {consistency['daily_entries']}
- Weekly plans: {consistency['weekly_plans']}
- Weekly reviews: {consistency['weekly_reviews']}

## Freetime focuses this month:
"""
    if freetime_focuses:
        for focus in freetime_focuses:
            content += f"- {focus}\n"
    else:
        content += "(No freetime focuses found)\n"

    content += "\n## Health:\n"
    content += f"- Sleep average: {sleep_data['average']:.1f} hours"
    if sleep_data['trend'] != 0.0:
        trend_sign = "+" if sleep_data['trend'] > 0 else ""
        content += f" (trend: {trend_sign}{sleep_data['trend']:.1f} vs last month)\n"
    else:
        content += " (no trend data)\n"
    content += f"- Days with mindful eating logged: {mindful_eating_days}\n"

    content += "\n## Weekly summaries:\n"
    for sunday, summary in weekly_summaries:
        content += f"\n### Week ending {(sunday + timedelta(days=6)).strftime('%B %d')}\n"
        for bullet in summary:
            content += f"- {bullet}\n"

    content += "\n## Monthly summary:\n"
    for bullet in monthly_summary:
        content += f"- {bullet}\n"

    content += "\n## Monthly reflection:\n"
    if monthly_reflection:
        content += f"{monthly_reflection}\n"

    return content
