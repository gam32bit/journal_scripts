#!/usr/bin/env python3
"""
Daily Journal - Create daily journal entry with tasks from weekly plan.
"""

import sys
from datetime import date
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, parser, templates, writer


def main():
    today = date.today()
    filepath = config.daily_path(today)
    
    # Check if already exists
    if filepath.exists():
        print(f"Today's journal already exists: {filepath}")
        print("Opening existing file...")
        writer.open_in_editor(filepath)
        
        # After editing, sync completed tasks
        process_completed_tasks(filepath)
        return
    
    # Find weekly plan
    weekly_path = config.weekly_path(today)
    weekly_file = weekly_path if weekly_path.exists() else None
    
    # Get data from weekly plan
    remaining_tasks = []
    focus_areas = []
    
    if weekly_file:
        print(f"Found weekly plan: {weekly_file}")
        remaining_tasks = writer.get_remaining_tasks(weekly_file)
        
        parsed = parser.parse_file(weekly_file)
        if parsed:
            focus_areas = parsed.get_list_items("focus")
        
        print(f"  {len(remaining_tasks)} tasks remaining")
        print(f"  {len(focus_areas)} focus areas")
    else:
        print("No weekly plan found for this week.")
    
    # Create daily journal
    content = templates.daily_journal_template(
        today,
        remaining_tasks,
        focus_areas,
        str(weekly_file) if weekly_file else None,
    )
    writer.write_file(filepath, content)
    
    print("Opening in editor...")
    writer.open_in_editor(filepath)
    
    # After editing, sync completed tasks
    process_completed_tasks(filepath)
    
    print("Journal entry saved!")


def process_completed_tasks(daily_file: Path):
    """Process completed tasks after editing."""
    # Get weekly file reference
    weekly_file = writer.extract_weekly_file_path(daily_file)
    
    if not weekly_file:
        # Fall back to calculating it
        weekly_file = config.weekly_path(date.today())
    
    if not weekly_file or not weekly_file.exists():
        return
    
    print("\nProcessing completed tasks...")
    completed = writer.sync_completed_tasks(daily_file, weekly_file)
    
    if completed:
        for task in completed:
            print(f"  ✓ Marked complete: {task}")
    else:
        print("  No new tasks to mark complete.")


if __name__ == "__main__":
    main()
