"""Writing/reflection entry command."""

import shutil
from datetime import date
from journal import config, parser, templates, ui, io


def scan_writings(date_strs: set) -> list[tuple]:
    """Scan WRITING_DIR and PUBLISH_DIR for files matching the given dates.

    Returns list of (title, status, source_url, source_title).
    Published status takes precedence if a file exists in both directories.
    """
    files = {}  # filename -> (path, status)

    for directory, status in [
        (config.WRITING_DIR, "draft"),
        (config.PUBLISH_DIR, "published"),
    ]:
        if not directory.exists():
            continue
        for filepath in sorted(directory.glob("*.md")):
            name = filepath.name
            if len(name) >= 10 and name[:10] in date_strs:
                if name not in files or status == "published":
                    files[name] = (filepath, status)

    results = []
    for name in sorted(files):
        filepath, status = files[name]
        parsed = parser.parse_file(filepath)
        stem = filepath.stem  # YYYY-MM-DD-slug
        title = stem[11:].replace("-", " ").title() if len(stem) > 11 else stem
        source_url = ""
        source_title = ""
        if parsed and parsed.front_matter:
            title = parsed.front_matter.get("title") or title
            source_url = parsed.front_matter.get("source_url", "") or ""
            source_title = parsed.front_matter.get("source_title", "") or ""
        results.append((title, status, source_url, source_title))

    return results


def run(target_date: date = None):
    """Create a writing/reflection entry."""
    if target_date is None:
        target_date = date.today()

    print("=== Writing ===\n")

    # Prompt for title (required)
    title = ""
    while not title:
        title = input("Title: ").strip()
        if not title:
            print("Title is required.")

    # Prompt for optional source URL
    source_url = input("Source URL (press Enter to skip): ").strip()
    source_title = ""
    if source_url:
        source_title = input("Source title (article/book name): ").strip()

    # Show writing ideas from current week's plan
    weekly_path = config.weekly_path(target_date)
    if weekly_path.exists():
        parsed = parser.parse_file(weekly_path)
        if parsed:
            writing_ideas = parsed.get_list_items("writing_ideas")
            if writing_ideas:
                print("\n=== Writing ideas from this week's plan ===")
                for idea in writing_ideas:
                    print(f"  - {idea}")
                print()

    # Create file from template
    filepath = config.writing_path(target_date, title)
    content = templates.writing_template(
        d=target_date,
        title=title,
        source_url=source_url,
        source_title=source_title,
    )
    io.write_file(filepath, content)

    # Open in editor with 15-minute timer
    print("\nOpening editor...")
    ui.open_in_editor(filepath, timer_minutes=15)

    # Prompt to publish
    publish = input("\nPublish now? (y/n): ").strip().lower()
    if publish == "y":
        config.PUBLISH_DIR.mkdir(parents=True, exist_ok=True)
        dest = config.PUBLISH_DIR / filepath.name
        shutil.copy2(filepath, dest)
        print(f"Published to: {dest}")
    else:
        print(f"Draft saved at: {filepath}")
