#!/usr/bin/env python3
"""
Monthly Plan - Create monthly planning template.
Run at the beginning of each month to set up the month.
"""

import sys
from datetime import date
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, templates, writer


def main():
    today = date.today()
    filepath = config.monthly_plan_path(today)

    # Check if already exists
    if filepath.exists():
        action = writer.handle_existing_file(filepath, "Monthly plan")
        if action != 'recreate':
            return

    print("=== Monthly Plan Setup ===")
    print("Opening monthly plan template in vim...")
    print("Fill in the sections and save when done.\n")

    # Create the monthly plan template with empty sections
    content = templates.monthly_plan_template(today, [], "", [])

    # Write the template file
    writer.write_file(filepath, content)

    # Open in vim for editing
    writer.open_in_editor(filepath)

    print(f"\nMonthly plan saved to: {filepath}")


if __name__ == "__main__":
    main()
