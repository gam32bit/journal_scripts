#!/usr/bin/env python3
"""
Journal - Weekly rhythm system.

Usage:
    journal.py              # Interactive menu
    journal.py day          # Create daily entry
    journal.py week plan    # Create weekly plan
    journal.py week review  # Create weekly review
    journal.py month plan   # Create monthly plan
    journal.py month review # Create monthly review
"""

import sys
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import commands


def main():
    args = sys.argv[1:]

    if not args:
        # Interactive menu mode
        run_interactive_menu()
        return

    # Subcommand mode
    cmd = " ".join(args).lower()

    command_map = {
        "day": commands.day,
        "daily": commands.day,  # alias
        "week plan": commands.week_plan,
        "week review": commands.week_review,
        "month plan": commands.month_plan,
        "month review": commands.month_review,
    }

    if cmd in command_map:
        command_map[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


def run_interactive_menu():
    """Run the interactive menu loop."""
    menu_options = {
        "1": ("Weekly Plan", commands.week_plan),
        "2": ("Daily Entry", commands.day),
        "3": ("Weekly Review", commands.week_review),
        "4": ("Monthly Plan", commands.month_plan),
        "5": ("Monthly Review", commands.month_review),
    }

    while True:
        print("\n=== Weekly Rhythm ===")
        for key, (label, _) in menu_options.items():
            print(f"{key}. {label}")
        print("0. Exit")
        print()

        choice = input("Select an option (0-5): ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        elif choice in menu_options:
            label, command_fn = menu_options[choice]
            print(f"\n--- {label} ---")
            command_fn()
            print()
        else:
            print("Invalid choice. Please select 0-5.")


if __name__ == "__main__":
    main()
