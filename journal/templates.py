"""
Templates for journal files.
Generates content for new entries.
"""

from datetime import date, timedelta


def daily_journal_template(
    d: date
) -> str:
    """Generate daily journal template."""

    return f"""
# Daily Entry - {d.strftime("%A, %B %d, %Y")}

---

## Journal entry:

"""


def weekly_review_template(
    d: date,
    daily_summaries: dict[str, list[str]],
    weekly_reflection: str,
    weekly_summary: list[str],
) -> str:
    """Generate weekly review content."""
    content = f"""# Weekly Review - {d.strftime("%B %d, %Y")}
"""
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
    weekly_reflections: list[tuple[date, str]],
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
- Weekly reviews: {consistency['weekly_reviews']}
"""

    content += "\n## Weekly reflections:\n"
    if weekly_reflections:
        for sunday, reflection in weekly_reflections:
            content += f"\n### Week ending {(sunday + timedelta(days=6)).strftime('%B %d')}\n"
            content += f"{reflection}\n"
    else:
        content += "(No weekly reflections found)\n"

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
