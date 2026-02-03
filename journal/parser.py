"""
Parser for journal files.
Handles section extraction with fallbacks for format variations.
"""

import re
from pathlib import Path
from .models import ParsedFile


# Section header patterns - normalize these to canonical names
SECTION_ALIASES = {
    # Weekly plan sections
    "what's coming up": "coming_up",
    "how i want to approach this week": "approach",
    "freetime focuses": "freetime",
    "freetime focuses (from monthly plan)": "freetime_monthly",
    "freetime focuses this week": "freetime",

    # Legacy freetime support (for older files)
    "focus areas": "freetime",

    # Daily journal sections
    "journal entry": "journal",
    "journal": "journal",
    "summary": "summary",

    # Weekly review sections
    "weekly reflection": "weekly_reflection",
    "weekly summary": "weekly_summary",
    "daily summaries": "daily_summaries",

    # Monthly plan sections
    "what's coming up this month": "coming_up_month",
    "themes or intentions": "themes",
    "freetime focuses to prioritize": "freetime",

    # Monthly review sections
    "consistency": "consistency",
    "monthly reflection": "monthly_reflection",
    "monthly summary": "monthly_summary",
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


def find_daily_files(d) -> list[Path]:
    """Find all daily journal files for the week containing date d."""
    from . import config

    files = []
    for day in config.get_week_dates(d):
        path = config.daily_path(day)
        if path.exists():
            files.append(path)
    return files
