# Weekly Rhythm System

> ⚠️ **Work in Progress** - This system is actively being developed and may change.

A Python-based weekly rhythm system for planning, daily check-ins, and review at weekly and monthly cadences.

## Overview

This system helps you maintain a sustainable weekly rhythm through planning, daily practice, and regular reflection:

| Command | Purpose | When to use |
|---------|---------|-------------|
| `journal.py` | Interactive menu to access all rhythm commands | Anytime |
| `journal.py month plan` | Create monthly plan with themes and priorities | Start of month |
| `journal.py week plan` | Create weekly plan with upcoming events and focuses | Sunday |
| `journal.py day` | Daily entry with summary bullets | Daily |
| `journal.py week review` | Aggregate the week's summaries into a review | Saturday |
| `journal.py month review` | Aggregate monthly data from weekly reviews | End of month |

## File Structure

Journal entries are stored in `~/entries/` organized by year and month:

```
~/entries/
└── 2025/
    └── 01/
        ├── monthly-plan-2025-01.md
        ├── weekly-2025-01-05.md
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
- Create a monthly plan
- Create a weekly plan
- Create a daily journal entry
- Generate a weekly review
- Generate a monthly review

### Direct Commands

You can also run commands directly:

#### Monthly Planning (Start of Month)

```bash
journal.py month plan
```

Opens a vim template with sections for:
- What's coming up this month (big events, deadlines, trips)
- Themes or intentions for the month
- Freetime focuses to prioritize

Shows last month's summary before opening vim for context.

If a monthly plan already exists, you'll be prompted to:
- **(e)dit** - Open the existing file in your editor
- **(r)ecreate** - Delete and create a new plan from scratch
- **(q)uit** - Cancel and exit

#### Weekly Planning (Sundays)

```bash
journal.py week plan
```

Prompts you for:
- What's coming up this week?
- How you want to approach this week (freeform)
- Freetime focuses for the week
- Eating intention (one concrete intention)

If a weekly plan already exists, you'll be prompted to:
- **(e)dit** - Open the existing file in your editor
- **(r)ecreate** - Delete and create a new plan from scratch
- **(q)uit** - Cancel and exit

#### Daily Entry

```bash
journal.py day
```

Creates a daily entry that:
- Prompts you for sleep hours
- Prompts for one mindful eating moment (optional)
- Shows your freetime focuses as reminders
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
- What came up this week (from weekly plan)
- Daily summaries organized by day
- Freetime focuses and reflection on them
- Health metrics (sleep average, mindful eating count)
- Prompts for weekly summary bullets

Offers ability to open specific daily entries for editing.

If a weekly review already exists, you'll be prompted to:
- **(e)dit** - Open the existing file in your editor
- **(r)ecreate** - Delete and create a new review from scratch
- **(q)uit** - Cancel and exit

#### Monthly Review (End of Month)

```bash
journal.py month review
```

Aggregates data from the entire month:
- **Consistency metrics**: Count of daily entries, weekly plans, and weekly reviews
- **What happened this month**: "What's coming up" from all weekly plans
- **All daily summaries**: Organized by week
- **Freetime focuses**: All unique focuses from weekly plans
- **Health**: Sleep average with trend, mindful eating count
- **Weekly summaries**: Bullets from all weekly reviews
- **Monthly summary prompts**: User writes bullets synthesizing the month

Offers ability to open specific weekly reviews for editing.

If a monthly review already exists, you'll be prompted to:
- **(e)dit** - Open the existing file in your editor
- **(r)ecreate** - Delete and create a new review from scratch
- **(q)uit** - Cancel and exit

## Configuration

Edit `journal/config.py` to change:
- `JOURNAL_DIR` - where journal files are stored (default: `~/entries`)
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
        ├── week_plan.py    # Weekly planning command
        ├── week_review.py  # Weekly review command
        ├── month_plan.py   # Monthly planning command
        └── month_review.py # Monthly review command
```

## Migration Notes

If you have existing journal files from the previous version:
- Old "focus areas" in weekly plans are automatically mapped to "freetime focuses"
- Old files with tags will still work (tags just won't be used)
- No data migration required, just new templates going forward

## Roadmap

- [x] Monthly plan script
- [x] Summary bullets instead of tags
- [ ] Sleep trend tracking (4-week rolling average)
- [ ] Migration tooling for batch converting old format files
