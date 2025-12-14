#!/usr/bin/env python3
"""
Weekly Plan - Create weekly planning template.
Run on Sundays to set up your week.
"""

import sys
from datetime import date
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, templates, writer


def main():
    today = date.today()
    filepath = config.weekly_path(today)
    
    # Check if already exists
    if filepath.exists():
        print(f"Weekly plan already exists: {filepath}")
        print("Opening existing file...")
        writer.open_in_editor(filepath)
        return
    
    # Create new weekly plan
    content = templates.weekly_plan_template(config.get_sunday(today))
    writer.write_file(filepath, content)
    
    print("Opening in editor...")
    writer.open_in_editor(filepath)
    
    print("Weekly plan saved!")


if __name__ == "__main__":
    main()
