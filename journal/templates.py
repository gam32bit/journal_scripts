"""
Templates for journal files.
Generates content for new entries.
"""

from datetime import date, timedelta


def writing_template(d: date, title: str, source_url: str = "", source_title: str = "") -> str:
    """Generate writing/reflection entry template."""
    source_url_val = source_url or ""
    source_title_val = source_title or ""

    content = f"""---
title: {title}
date: {d}
source_url: {source_url_val}
source_title: {source_title_val}
status: draft
---

# {title}

"""
    if source_url_val:
        display = source_title_val if source_title_val else source_url_val
        content += f"Source: [{display}]({source_url_val})\n\n"

    return content


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
    freetime_focuses: list[str],
) -> str:
    """Generate daily journal template."""

    # Format freetime focuses
    if freetime_focuses:
        freetime_str = "\n".join(f"- {focus}" for focus in freetime_focuses)
    else:
        freetime_str = "(No freetime focuses defined)"

    return f"""---
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
    freetime_focuses: list[str],
    daily_summaries: dict[str, list[str]],
    weekly_reflection: str,
    weekly_summary: list[str],
    writings: list[tuple] = None,
) -> str:
    """Generate weekly review content."""
    content = f"""# Weekly Review - {d.strftime("%B %d, %Y")}

## Freetime focuses:
"""
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

    if writings:
        reading_reflections = [(t, s, su, st) for t, s, su, st in writings if su and su.strip()]
        other_writings = [(t, s, su, st) for t, s, su, st in writings if not (su and su.strip())]

        if reading_reflections:
            content += "\n## Reading reflections this week:\n"
            for title, status, source_url, source_title in reading_reflections:
                ref = source_title if source_title and source_title.strip() else source_url
                content += f'- "{title}" (re: {ref}) ({status})\n'

        if other_writings:
            content += "\n## Writing this week:\n"
            for title, status, source_url, source_title in other_writings:
                content += f'- "{title}" ({status})\n'

    return content


def monthly_review_template(
    d: date,
    consistency: dict,
    freetime_focuses: list[str],
    weekly_reflections: list[tuple[date, str]],
    weekly_summaries: list[tuple[date, list[str]]],
    monthly_summary: list[str],
    monthly_reflection: str,
    writings: list[tuple] = None,
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

    if writings:
        published = [(t, s, su, st) for t, s, su, st in writings if s == "published"]
        drafts = [(t, s, su, st) for t, s, su, st in writings if s == "draft"]
        content += f"\n## Writing this month ({len(published)} published, {len(drafts)} draft):\n"
        for title, status, source_url, source_title in writings:
            content += f'- "{title}" ({status})\n'

    content += "\n## Monthly summary:\n"
    for bullet in monthly_summary:
        content += f"- {bullet}\n"

    content += "\n## Monthly reflection:\n"
    if monthly_reflection:
        content += f"{monthly_reflection}\n"

    return content
