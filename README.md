# CLI Journaling System

> ⚠️ **Work in Progress** - This system is actively being developed and may change.

A Python-based reflection system for daily check-ins and weekly/monthly review.

## Overview

This system helps you maintain a sustainable reflection rhythm through daily practice and regular review:

| Command | Purpose | When to use |
|---------|---------|-------------|
| `journal.py` | Interactive menu to access all reflection commands | Anytime |
| `journal.py day` | Daily entry with summary bullets | Daily |
| `journal.py week review` | Aggregate the week's summaries into a review | Saturday |
| `journal.py month review` | Aggregate monthly data from weekly reviews | End of month |

## File Structure

Journal entries are stored in `~/entries/` organized by year and month:

```
~/entries/
└── 2025/
    └── 01/
        ├── daily-2025-01-06.md
        ├── daily-2025-01-07.md
        ├── review-2025-01-11.md
        └── monthly-2025-01.md
```

## Installation

```bash
# Clone the repo
git clone git@github.com:gam32bit/journal_scripts.git ~/scripts

# Make entry point executable
chmod +x ~/scripts/journal.py

# Add to PATH (add to ~/.bashrc)
export PATH="$HOME/scripts:$PATH"
```

## Usage

### Interactive Menu (Recommended)

```bash
journal.py
```

Launches an interactive menu where you can:
- Create a daily journal entry
- Generate a weekly review
- Generate a monthly review

### The `--date` Flag

By default, all commands target today's date. Use `--date YYYY-MM-DD` to target a specific date instead — useful for catching up on missed entries or running reviews retroactively:

```bash
journal.py week review --date 2025-02-07   # Run last week's review using Saturday's date
journal.py day --date 2025-02-06            # Backfill a daily entry for Thursday
journal.py --date 2025-01-31 month review   # Run January's monthly review
```

The flag can appear anywhere in the argument list (before or after the command name) and also works with the interactive menu.

### Direct Commands

You can also run commands directly:

#### Daily Entry

```bash
journal.py day
```

Creates a daily entry that:
- Opens default editor to write journal entry
- Prompts for 2-3 summary bullets that capture the texture of the day

Summary bullets are what get aggregated in weekly and monthly reviews (e.g., "Fun family visit", "Weird unexplained lethargy").

If a journal entry already exists, you'll be prompted to:
- **(e)dit** - Open the existing file in your editor
- **(r)ecreate** - Delete and create a new entry from scratch
- **(q)uit** - Cancel and exit

#### Weekly Review (Saturdays)

```bash
journal.py week review
```

Aggregates the week's data:
- Daily summaries organized by day
- Prompts for a weekly reflection ("how did this week go?")
- Prompts for 3-5 weekly summary bullets

If a weekly review already exists, you'll be prompted to:
- **(e)dit** - Open the existing file in your editor
- **(r)ecreate** - Delete and create a new review from scratch
- **(q)uit** - Cancel and exit

#### Monthly Review (End of Month)

```bash
journal.py month review
```

Aggregates data from the entire month:
- **Consistency metrics**: Count of daily entries and weekly reviews
- **Weekly reflections**: "How did this week go?" reflections from each weekly review
- **Weekly summaries**: Bullets from all weekly reviews
- **Monthly summary prompts**: User writes bullets synthesizing the month
- **Monthly reflection**: "How did this month go?"

Offers ability to open specific weekly reviews for editing.

If a monthly review already exists, you'll be prompted to:
- **(e)dit** - Open the existing file in your editor
- **(r)ecreate** - Delete and create a new review from scratch
- **(q)uit** - Cancel and exit

## Configuration

Edit `journal/config.py` to change:
- `JOURNAL_DIR` - where journal files are stored (default: `~/.entries_encrypted/`)
- `EDITOR` - which editor to use (default: `$EDITOR` or `vim`)

## Code Structure

The codebase is organized as a single entry point with modular components:

```
journal_scripts/
├── journal.py              # Single entry point with subcommands
├── README.md
├── .gitignore
└── journal/
    ├── __init__.py
    ├── config.py           # Paths and constants
    ├── models.py           # ParsedFile dataclass
    ├── parser.py           # Parsing logic
    ├── templates.py        # Templates for journal files
    ├── io.py               # File I/O operations
    ├── ui.py               # User interaction (prompts, editor, menus)
    └── commands/
        ├── __init__.py
        ├── base.py         # Shared command infrastructure
        ├── day.py          # Daily entry command
        ├── week_review.py  # Weekly review command
        └── month_review.py # Monthly review command
```

## Roadmap

- [x] Summary bullets instead of tags
