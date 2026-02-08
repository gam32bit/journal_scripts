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

Options:
    --date YYYY-MM-DD       Target a specific date instead of today
"""

import sys
from datetime import datetime
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import commands


def parse_date_flag(args):
    """Extract --date YYYY-MM-DD from args, returning (remaining_args, target_date).

    Returns the args list with --date and its value removed, and the parsed date
    (or None if --date was not provided).
    """
    if "--date" not in args:
        return args, None

    idx = args.index("--date")

    if idx + 1 >= len(args):
        print("Error: --date requires a value in YYYY-MM-DD format.")
        sys.exit(1)

    date_str = args[idx + 1]

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"Error: Invalid date '{date_str}'. Expected format: YYYY-MM-DD.")
        sys.exit(1)

    remaining = args[:idx] + args[idx + 2:]
    return remaining, target_date


def main():
    args = sys.argv[1:]

    # Extract --date flag before processing commands
    args, target_date = parse_date_flag(args)

    if not args:
        # Interactive menu mode
        run_interactive_menu(target_date=target_date)
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
        kwargs = {}
        if target_date is not None:
            kwargs["target_date"] = target_date
        command_map[cmd](**kwargs)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


def run_interactive_menu(target_date=None):
    """Run the interactive menu loop."""
    menu_options = {
        "1": ("Weekly Plan", commands.week_plan),
        "2": ("Daily Entry", commands.day),
        "3": ("Weekly Review", commands.week_review),
        "4": ("Monthly Plan", commands.month_plan),
        "5": ("Monthly Review", commands.month_review),
    }

    while True:
        header = "=== Weekly Rhythm ==="
        if target_date is not None:
            header = f"=== Weekly Rhythm (date: {target_date}) ==="
        print(f"\n{header}")
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
            kwargs = {}
            if target_date is not None:
                kwargs["target_date"] = target_date
            command_fn(**kwargs)
            print()
            break  # Exit after completing the command
        else:
            print("Invalid choice. Please select 0-5.")


if __name__ == "__main__":
    main()
