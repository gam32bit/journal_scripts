"""
Data models for journal system.
ParsedFile dataclass and related types.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ParsedFile:
    """Result of parsing a journal file."""
    filepath: Path
    sections: dict[str, list[str]] = field(default_factory=dict)
    raw_lines: list[str] = field(default_factory=list)
    front_matter: dict[str, str] = field(default_factory=dict)

    def get_section(self, name: str) -> list[str]:
        """Get section content by canonical name."""
        return self.sections.get(name, [])

    def get_section_text(self, name: str) -> str:
        """Get section as joined text, stripped."""
        lines = self.get_section(name)
        return "\n".join(lines).strip()

    def get_list_items(self, name: str) -> list[str]:
        """Get section as list items (lines starting with -)."""
        items = []
        for line in self.get_section(name):
            stripped = line.strip()
            if stripped.startswith("- "):
                item = stripped[2:].strip()
                if item:  # Skip empty items
                    items.append(item)
        return items

    def get_front_matter(self, key: str) -> str | None:
        """Get a value from the YAML front matter."""
        return self.front_matter.get(key)

    def get_checked_items(self, name: str) -> tuple[list[str], list[str]]:
        """
        Get checked and unchecked items from a section.
        Returns (checked, unchecked) tuple.
        Supports: [x] or [X] for checked, [ ] or - for unchecked
        """
        checked = []
        unchecked = []

        for line in self.get_section(name):
            stripped = line.strip()

            # [x] or [X] = checked
            if re.match(r"^-?\s*\[[xX]\]\s*", stripped):
                item = re.sub(r"^-?\s*\[[xX]\]\s*", "", stripped).strip()
                if item:
                    checked.append(item)
            # [ ] = unchecked
            elif re.match(r"^-?\s*\[\s*\]\s*", stripped):
                item = re.sub(r"^-?\s*\[\s*\]\s*", "", stripped).strip()
                if item:
                    unchecked.append(item)
            # Plain - item = unchecked
            elif stripped.startswith("- "):
                item = stripped[2:].strip()
                if item:
                    unchecked.append(item)

        return checked, unchecked

    def get_summary_bullets(self) -> list[str]:
        """Get summary bullets from front matter or section."""
        # Try front matter first
        fm_summary = self.get_front_matter("summary")
        if fm_summary:
            # Parse list format: [bullet1, bullet2, bullet3]
            fm_summary = fm_summary.strip()
            if fm_summary.startswith("[") and fm_summary.endswith("]"):
                fm_summary = fm_summary[1:-1]
            bullets = [bullet.strip() for bullet in fm_summary.split(",") if bullet.strip()]
            return bullets

        # Fall back to section
        return self.get_list_items("summary")

    def get_sleep_hours(self) -> str | None:
        """Extract sleep hours from front matter."""
        return self.get_front_matter("sleep_hours")

    def get_eating_reflection(self) -> str | None:
        """Extract eating reflection from front matter (legacy)."""
        return self.get_front_matter("eating_reflection")

    def get_mindful_eating(self) -> str | None:
        """Extract mindful eating moment from front matter."""
        return self.get_front_matter("mindful_eating")

    def get_sleep_score(self) -> str | None:
        """Extract sleep score (X, -, or O)."""
        text = self.get_section_text("sleep")
        if not text:
            return None

        # Look for X, -, or O
        text_upper = text.upper()
        for char in ["O", "-", "X"]:
            if char in text_upper:
                return char

        # Also accept Good/Decent/Bad
        text_lower = text.lower()
        if "good" in text_lower:
            return "O"
        if "decent" in text_lower:
            return "-"
        if "bad" in text_lower:
            return "X"

        return None
