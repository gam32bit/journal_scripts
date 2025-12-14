#!/usr/bin/env python3
"""
Daily Prompt - Create daily writing entry with prompts from weekly plan.
"""

import sys
from datetime import date
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, parser, templates, writer


def main():
    today = date.today()
    filepath = config.prompt_path(today)
    
    # Check if already exists
    if filepath.exists():
        print(f"Today's prompt already exists: {filepath}")
        print("Opening existing file...")
        writer.open_in_editor(filepath)
        return
    
    # Find weekly plan
    weekly_path = config.weekly_path(today)
    weekly_file = weekly_path if weekly_path.exists() else None
    
    # Get writing prompts from weekly plan
    writing_prompts = []
    
    if weekly_file:
        print(f"Found weekly plan: {weekly_file}")
        parsed = parser.parse_file(weekly_file)
        if parsed:
            writing_prompts = parsed.get_list_items("prompts")
        print(f"  {len(writing_prompts)} writing prompts")
    else:
        print("No weekly plan found for this week.")
    
    # Create daily prompt
    content = templates.daily_prompt_template(
        today,
        writing_prompts,
        str(weekly_file) if weekly_file else None,
    )
    writer.write_file(filepath, content)
    
    print("Opening in editor...")
    writer.open_in_editor(filepath)
    
    print("Writing entry saved!")


if __name__ == "__main__":
    main()
