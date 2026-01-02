"""
Parser for journal files.
Handles section extraction with fallbacks for format variations.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field


# Section header patterns - normalize these to canonical names
SECTION_ALIASES = {
    # Weekly plan sections
    "focus areas": "focus",
    "focus areas (mood/habits)": "focus",
    "focus": "focus",
    "eating intention": "eating_intention",

    # Daily journal sections
    "sleep quality": "sleep",
    "sleep": "sleep",
    "sleep hours": "sleep_hours",
    "yesterday's eating reflection": "eating",
    "eating reflection": "eating",
    "eating": "eating",
    "journal entry": "journal",
    "journal": "journal",
    "tags": "tags",

    # Review sections
    "weekly reflection": "reflection",

    # Monthly review sections
    "consistency": "consistency",
    "emotional landscape": "emotional_landscape",
    "focus areas this month": "focus_areas_month",
    "eating intentions this month": "eating_intentions_month",
    "monthly reflection": "monthly_reflection",
}


def normalize_header(line: str) -> str | None:
    """
    Convert a header line to its canonical section name.
    Returns None if not a recognized header.
    """
    # Strip common header markers
    cleaned = line.strip().lower()
    cleaned = cleaned.lstrip("#").strip()
    cleaned = cleaned.strip("-=").strip()
    
    # If there's a colon, only look at the part before it for matching
    if ":" in cleaned:
        prefix = cleaned.split(":")[0].strip()
        prefix_with_colon = prefix + ":"
        # Try with colon first (some aliases include it)
        if prefix_with_colon.rstrip(":") in SECTION_ALIASES:
            return SECTION_ALIASES[prefix_with_colon.rstrip(":")]
        if prefix in SECTION_ALIASES:
            return SECTION_ALIASES[prefix]
    
    # Try the full cleaned string
    cleaned_no_colon = cleaned.rstrip(":").strip()
    return SECTION_ALIASES.get(cleaned_no_colon)


def is_section_header(line: str) -> bool:
    """Check if line looks like a section header."""
    stripped = line.strip()
    if not stripped:
        return False
    
    # Check for common header patterns
    if stripped.startswith("#"):
        return True
    if stripped.startswith("[") and stripped.endswith("]"):
        return True
    # All caps line ending with colon
    if stripped.rstrip(":").isupper() and ":" in stripped:
        return True
    
    # Check if it matches a known alias (check prefix before colon)
    if ":" in stripped:
        prefix = stripped.split(":")[0].strip()
        if normalize_header(prefix + ":"):
            return True
    
    # Standalone line matching alias
    if normalize_header(stripped):
        return True
    
    return False


def is_separator(line: str) -> bool:
    """Check if line is a visual separator (===, ---, etc)."""
    stripped = line.strip()
    if len(stripped) < 3:
        return False
    return all(c in "=-_" for c in stripped)


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
    
    def get_tags(self) -> list[str]:
        """Extract tags from the front matter or tags section."""
        # First try front matter
        fm_tags = self.get_front_matter("tags")
        if fm_tags:
            # Parse the list format: [tag1, tag2, tag3]
            fm_tags = fm_tags.strip()
            if fm_tags.startswith("[") and fm_tags.endswith("]"):
                fm_tags = fm_tags[1:-1]
            tags = [tag.strip().lower() for tag in fm_tags.split(",") if tag.strip()]
            return tags

        # Fall back to tags section
        text = self.get_section_text("tags")
        if not text:
            return []

        # Handle "Tags: tag1, tag2, tag3" format
        if ":" in text.split("\n")[0]:
            text = text.split(":", 1)[1]

        # Split by comma, clean up
        tags = []
        for tag in text.replace("\n", ",").split(","):
            cleaned = tag.strip().lower()
            # Remove # if present
            cleaned = cleaned.lstrip("#").strip()
            if cleaned:
                tags.append(cleaned)

        return tags

    def get_sleep_hours(self) -> str | None:
        """Extract sleep hours from front matter."""
        return self.get_front_matter("sleep_hours")

    def get_eating_reflection(self) -> str | None:
        """Extract eating reflection from front matter."""
        return self.get_front_matter("eating_reflection")
    
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


def parse_file(filepath: Path) -> ParsedFile | None:
    """
    Parse a journal file into sections.
    Returns None if file doesn't exist.
    """
    if not filepath.exists():
        return None

    result = ParsedFile(filepath=filepath)

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            result.raw_lines = f.readlines()
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return None

    # Parse YAML front matter if present
    in_front_matter = False
    front_matter_lines = []
    content_start_idx = 0

    if result.raw_lines and result.raw_lines[0].strip() == "---":
        in_front_matter = True
        content_start_idx = 1

        for i in range(1, len(result.raw_lines)):
            line = result.raw_lines[i]
            if line.strip() == "---":
                content_start_idx = i + 1
                break
            front_matter_lines.append(line)

        # Parse front matter lines
        for line in front_matter_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                result.front_matter[key.strip()] = value.strip()

    current_section = None
    current_content = []

    for line in result.raw_lines[content_start_idx:]:
        # Skip separators
        if is_separator(line):
            continue
        
        # Skip metadata references like [weekly_file:...]
        stripped = line.strip()
        if stripped.startswith("[") and ":" in stripped and stripped.endswith("]"):
            if not stripped.lower().startswith("[completed"):
                continue
        
        # Check for section header
        if is_section_header(line):
            # Save previous section
            if current_section:
                result.sections[current_section] = current_content
            
            # Start new section
            canonical = normalize_header(line)
            if canonical:
                current_section = canonical
                current_content = []
                
                # Check for inline value (e.g., "Sleep quality: O")
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        inline_value = parts[1].strip()
                        if inline_value:
                            current_content.append(inline_value)
            else:
                # Unknown header - keep content with previous section
                if current_section:
                    current_content.append(line)
        else:
            # Regular content line
            if current_section:
                current_content.append(line.rstrip("\n"))
    
    # Save final section
    if current_section:
        result.sections[current_section] = current_content
    
    return result


def find_weekly_file(d) -> Path | None:
    """
    Find the weekly plan file for the week containing date d.
    Returns path if exists, None otherwise.
    """
    from . import config
    
    path = config.weekly_path(d)
    return path if path.exists() else None


def find_daily_files(d) -> list[Path]:
    """Find all daily journal files for the week containing date d."""
    from . import config

    files = []
    for day in config.get_week_dates(d):
        path = config.daily_path(day)
        if path.exists():
            files.append(path)
    return files
