"""
Templates for journal files.
Generates content for new entries.
"""

from datetime import date


def weekly_plan_template(d: date, coming_up: list[str], approach: str, freetime: list[str], eating_intention: str) -> str:
    """Generate weekly plan template."""
    coming_up_str = "\n".join(f"- {item}" for item in coming_up) if coming_up else "- "
    freetime_str = "\n".join(f"- {item}" for item in freetime) if freetime else "- "

    return f"""# Weekly Plan
Week of: {d.strftime("%B %d, %Y")}

## What's coming up:
{coming_up_str}

## How I want to approach this week:
{approach if approach else ""}

## Freetime focuses:
{freetime_str}

## Eating intention:
{eating_intention if eating_intention else ""}
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

# Daily Entry
Date: {d.strftime("%A, %B %d, %Y")}

## Freetime focuses:
{freetime_str}

---

## Journal entry:


---

## Summary:
-
-
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
