#!/usr/bin/env python3
"""
Daily Journal - Create daily journal entry.
"""

import sys
import re
import tempfile
from datetime import date
from pathlib import Path

# Add parent dir to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from journal import config, parser, writer


def load_emotion_tags() -> set[str]:
    """Load emotion tags from the tags file."""
    tags_file = Path(__file__).parent / "emotion_tags.txt"
    if not tags_file.exists():
        return set()

    with open(tags_file, "r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}


def detect_tags_in_text(text: str, emotion_tags: set[str]) -> list[str]:
    """Detect emotion tags in text, including variations."""
    detected = set()
    text_lower = text.lower()

    # Split text into words, removing punctuation
    words = re.findall(r'\b\w+\b', text_lower)

    for word in words:
        # Check exact match
        if word in emotion_tags:
            detected.add(word)
            continue

        # Check if word is a variation of a tag
        for tag in emotion_tags:
            # Handle common variations
            # e.g., "enjoying" -> "joy", "stressed" -> "stress"
            if tag in word or word in tag:
                # Additional check to avoid false positives
                if abs(len(word) - len(tag)) <= 3:  # Similar length
                    detected.add(tag)

    return sorted(list(detected))


def get_eating_intention(today: date) -> str | None:
    """Get eating intention from weekly plan."""
    weekly_path = config.weekly_path(today)
    if not weekly_path.exists():
        return None

    parsed = parser.parse_file(weekly_path)
    if not parsed:
        return None

    return parsed.get_section_text("eating_intention")


def main():
    today = date.today()
    filepath = config.daily_path(today)

    # Check if already exists
    if filepath.exists():
        action = writer.handle_existing_file(filepath, "Today's journal")
        if action != 'recreate':
            return

    print("=== Daily Journal Entry ===\n")

    # Get sleep hours
    sleep_hours = input("How many hours did you sleep last night? ").strip()

    # Get eating intention from weekly plan
    print("\n--- This Week's Eating Intention ---")
    eating_intention = get_eating_intention(today)
    if eating_intention:
        print(eating_intention)
    else:
        print("No eating intention found for this week.")

    # Get eating reflection
    print("\n--- Today's Eating Reflection ---")
    eating_reflection = input("Enter your eating reflection for today: ").strip()

    # Find weekly plan for focus areas
    weekly_path = config.weekly_path(today)
    focus_areas = []

    if weekly_path.exists():
        parsed = parser.parse_file(weekly_path)
        if parsed:
            focus_areas = parsed.get_list_items("focus")

    # Create initial journal template
    focus_str = "\n".join(f"- {area}" for area in focus_areas) if focus_areas else "(No focus areas defined)"

    content = f"""---
sleep_hours: {sleep_hours}
eating_reflection: {eating_reflection}
tags: []
---

# Daily Journal
Date: {today.strftime("%A, %B %d, %Y")}

## Focus areas:
{focus_str}

---

## Journal entry:

"""

    # Write initial file
    writer.write_file(filepath, content)

    # Open in editor for user to write entry
    print("\nOpening editor for journal entry...")
    writer.open_in_editor(filepath)

    # After editor closes, read the file and detect tags
    print("\n--- Tag Detection ---")
    if not filepath.exists():
        print("Journal file not found. Exiting.")
        return

    # Read the journal content
    file_content = filepath.read_text(encoding="utf-8")

    # Extract the journal entry section
    parsed = parser.parse_file(filepath)
    if parsed:
        journal_text = parsed.get_section_text("journal")
    else:
        journal_text = ""

    # Print the entry
    print("\nYour journal entry:")
    print("-" * 50)
    print(journal_text)
    print("-" * 50)

    # Detect tags
    emotion_tags = load_emotion_tags()
    detected_tags = detect_tags_in_text(journal_text, emotion_tags)

    if detected_tags:
        print(f"\nDetected tags: {', '.join(detected_tags)}")
        edit_tags = input("Edit these tags? (y/n): ").strip().lower()

        if edit_tags == 'y':
            # Create a temporary file with tags for editing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp:
                tmp_path = Path(tmp.name)
                # Write tags one per line with instructions
                tmp.write("# Edit the tags below (one per line)\n")
                tmp.write("# Remove any tags you don't want\n")
                tmp.write("# Lines starting with # are ignored\n\n")
                for tag in detected_tags:
                    tmp.write(f"{tag}\n")

            # Open in editor
            print("Opening editor to review tags...")
            writer.open_in_editor(tmp_path)

            # Read back the edited tags
            edited_content = tmp_path.read_text(encoding='utf-8')
            tags = [
                line.strip().lower()
                for line in edited_content.split('\n')
                if line.strip() and not line.strip().startswith('#')
            ]

            # Clean up temp file
            tmp_path.unlink()

            print(f"\nFinal tags: {', '.join(tags) if tags else '(none)'}")
        else:
            tags = detected_tags

        # Ask if they want to add more tags
        add_more = input("Add additional tags? (y/n): ").strip().lower()
        if add_more == 'y':
            additional = input("Enter additional tags (comma-separated): ").strip()
            if additional:
                additional_tags = [tag.strip().lower() for tag in additional.split(",") if tag.strip()]
                tags = tags + additional_tags
    else:
        print("No emotion tags detected.")
        add_tags = input("Would you like to add tags manually? (y/n): ").strip().lower()

        if add_tags == 'y':
            print("\nYour journal entry:")
            print("-" * 50)
            print(journal_text)
            print("-" * 50)
            manual_tags = input("\nEnter tags (comma-separated): ").strip()
            tags = [tag.strip().lower() for tag in manual_tags.split(",") if tag.strip()]
        else:
            tags = []

    # Update the front matter with tags
    tags_str = ", ".join(tags)
    updated_content = re.sub(
        r'tags: \[\]',
        f'tags: [{tags_str}]',
        file_content
    )

    filepath.write_text(updated_content, encoding="utf-8")
    print(f"\nJournal entry saved with {len(tags)} tags!")


if __name__ == "__main__":
    main()
