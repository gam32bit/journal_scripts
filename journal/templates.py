"""
Templates for journal files.
Generates content for new entries.
"""

from datetime import date


def weekly_plan_template(d: date) -> str:
    """Generate weekly plan template."""
    return f"""# Weekly Plan
Week of: {d.strftime("%B %d, %Y")}

## Tasks for this week:
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

## Focus areas:
- 
- 

## Writing prompts:
- 
- 
- 

---
[completed_tasks]

"""


def daily_journal_template(
    d: date,
    remaining_tasks: list[str],
    focus_areas: list[str],
    weekly_file: str | None = None,
) -> str:
    """Generate daily journal template."""
    
    # Format tasks as checkboxes
    if remaining_tasks:
        tasks_str = "\n".join(f"- [ ] {task}" for task in remaining_tasks)
    else:
        tasks_str = "(No tasks defined or all complete)"
    
    # Format focus areas
    if focus_areas:
        focus_str = "\n".join(f"- {area}" for area in focus_areas)
    else:
        focus_str = "(No focus areas defined)"
    
    weekly_ref = f"\n[weekly_file:{weekly_file}]" if weekly_file else ""
    
    return f"""# Daily Journal
Date: {d.strftime("%A, %B %d, %Y")}

## Weekly tasks remaining:
{tasks_str}

## Focus areas:
{focus_str}

---

## Sleep quality: 

## Yesterday's eating reflection:


## Journal entry:


## Tags: 
{weekly_ref}
"""


def daily_prompt_template(
    d: date,
    writing_prompts: list[str],
    weekly_file: str | None = None,
) -> str:
    """Generate daily writing prompt template."""
    
    if writing_prompts:
        prompts_str = "\n".join(f"- {prompt}" for prompt in writing_prompts)
    else:
        prompts_str = "(No prompts defined this week)"
    
    weekly_ref = f"\n[weekly_file:{weekly_file}]" if weekly_file else ""
    
    return f"""# Daily Writing
Date: {d.strftime("%A, %B %d, %Y")}

## Available prompts this week:
{prompts_str}

---

## Today's prompt:


## Writing:


{weekly_ref}
"""


def weekly_review_template(
    d: date,
    daily_count: int,
    prompt_count: int,
    sleep_avg: float | None,
    sleep_scores: list[tuple[str, str | None]],  # (day_name, score)
    eating_reflections: list[tuple[str, str]],   # (date_str, text)
    tag_frequency: list[tuple[str, int]],        # (tag, count)
    tag_timeline: dict[str, list[str]],          # tag -> [day_names]
    writing_excerpts: list[tuple[str, str, str]], # (date_str, prompt, excerpt)
    completed_tasks: list[str],
    incomplete_tasks: list[str],
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
    
    # Writing excerpts
    if writing_excerpts:
        writing_lines = []
        for date_str, prompt, excerpt in writing_excerpts:
            writing_lines.append(f"[{date_str}]")
            writing_lines.append(f"Prompt: {prompt if prompt else '(not specified)'}")
            if excerpt:
                writing_lines.append("Excerpt:")
                for line in excerpt.split("\n")[:3]:
                    writing_lines.append(f"  {line}")
            writing_lines.append("")
        writing_str = "\n".join(writing_lines)
    else:
        writing_str = "(No writing this week)"
    
    # Tasks
    if completed_tasks:
        completed_str = "\n".join(f"  ✓ {task}" for task in completed_tasks)
    else:
        completed_str = "  (none)"
    
    if incomplete_tasks:
        incomplete_str = "\n".join(f"  ○ {task}" for task in incomplete_tasks)
    else:
        incomplete_str = "  (none - great job!)"
    
    # Focus areas
    if focus_areas:
        focus_str = "\n".join(f"- {area}" for area in focus_areas)
    else:
        focus_str = "(No focus areas defined)"
    
    return f"""# Weekly Review
Week ending: {d.strftime("%B %d, %Y")}

Daily entries found: {daily_count}
Writing entries found: {prompt_count}

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

## Writing this week:
{writing_str}

## Task completion:

Completed:
{completed_str}

Incomplete:
{incomplete_str}

## Focus areas this week:
{focus_str}

---

## Weekly reflection:

How did you do with your focus areas this week?


What went well this week?


What could be improved?


Key insights or lessons learned:


"""
