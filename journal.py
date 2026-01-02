#!/usr/bin/env python3
"""
Journal - Main menu for journal system.
Run this to access plan, daily entry, or review.
"""

import sys
import subprocess
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))


def show_menu():
    """Display the main menu."""
    print("\n=== Weekly Rhythm ===")
    print("1. Weekly Plan")
    print("2. Daily Entry")
    print("3. Weekly Review")
    print("4. Monthly Plan")
    print("5. Monthly Review")
    print("0. Exit")
    print()


def main():
    script_dir = Path(__file__).parent

    while True:
        show_menu()
        choice = input("Select an option (0-5): ").strip()

        if choice == "1":
            print("\n--- Weekly Plan ---")
            subprocess.run([sys.executable, str(script_dir / "j-plan.py")])
            print()
        elif choice == "2":
            print("\n--- Daily Entry ---")
            subprocess.run([sys.executable, str(script_dir / "j-daily.py")])
            print()
        elif choice == "3":
            print("\n--- Weekly Review ---")
            subprocess.run([sys.executable, str(script_dir / "j-review.py")])
            print()
        elif choice == "4":
            print("\n--- Monthly Plan ---")
            subprocess.run([sys.executable, str(script_dir / "j-month-plan.py")])
            print()
        elif choice == "5":
            print("\n--- Monthly Review ---")
            subprocess.run([sys.executable, str(script_dir / "j-monthly.py")])
            print()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 0-5.")


if __name__ == "__main__":
    main()
