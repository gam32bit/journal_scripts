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
    journal.py write        # Create writing/reflection entry
    journal.py stats        # Show journal and writing stats

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
        "write": commands.write,
        "stats": commands.stats,
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
    kwargs = {}
    if target_date is not None:
        kwargs["target_date"] = target_date

    while True:
        header = "=== Weekly Rhythm ==="
        if target_date is not None:
            header = f"=== Weekly Rhythm (date: {target_date}) ==="
        print(f"\n{header}")
        print("1. Daily Entry")
        print("2. Weekly")
        print("3. Monthly")
        print("4. Writing")
        print("5. Stats")
        print("0. Exit")
        print()

        choice = input("Select an option (0-5): ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            commands.day(**kwargs)
            print()
            break
        elif choice == "2":
            print("\n--- Weekly ---")
            print("1. Plan")
            print("2. Review")
            print("0. Back")
            print()
            sub = input("Select an option (0-2): ").strip()
            if sub == "0":
                continue
            elif sub == "1":
                commands.week_plan(**kwargs)
                print()
                break
            elif sub == "2":
                commands.week_review(**kwargs)
                print()
                break
            else:
                print("Invalid choice. Please select 0-2.")
        elif choice == "3":
            print("\n--- Monthly ---")
            print("1. Plan")
            print("2. Review")
            print("0. Back")
            print()
            sub = input("Select an option (0-2): ").strip()
            if sub == "0":
                continue
            elif sub == "1":
                commands.month_plan(**kwargs)
                print()
                break
            elif sub == "2":
                commands.month_review(**kwargs)
                print()
                break
            else:
                print("Invalid choice. Please select 0-2.")
        elif choice == "4":
            commands.write(**kwargs)
            print()
            break
        elif choice == "5":
            commands.stats(**kwargs)
            print()
            break
        else:
            print("Invalid choice. Please select 0-5.")


if __name__ == "__main__":
    main()
