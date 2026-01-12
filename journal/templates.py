"""
Templates for journal files.
Generates content for new entries.
"""

from datetime import date


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
