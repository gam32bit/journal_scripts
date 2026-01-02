# Journal Scripts

> ⚠️ **Work in Progress** - This system is actively being developed and may change.

A Python-based personal journaling system for weekly planning, daily journaling, and reflection.

## Overview

This system connects weekly intentions with daily practice through an interactive menu or individual scripts:

| Script | Purpose | When to use |
|--------|---------|-------------|
| `journal.py` | Interactive menu to access all journal commands | Anytime |
| `j-plan.py` | Create weekly plan with tasks and focus areas | Sunday |
| `j-daily.py` | Daily journal with tasks pulled from weekly plan | Daily |
| `j-review.py` | Aggregate the week's data into a review document | Saturday |
| `j-monthly.py` | Aggregate monthly data from weekly reviews into a summary | End of month |

## File Structure

Journal entries are stored in `~/entries/` organized by year and month:

```
~/entries/
└── 2025/
    └── 12/
        ├── weekly-2025-12-14.md
        ├── daily-2025-12-15.md
        ├── daily-2025-12-16.md
        ├── review-2025-12-20.md
        └── monthly-2025-12.md
```

## Installation

```bash
# Clone the repo
git clone git@github.com:gam32bit/journal_scripts.git ~/scripts

# Make entry points executable
chmod +x ~/scripts/journal.py ~/scripts/j-*.py

# Add to PATH (add to ~/.bashrc)
export PATH="$HOME/scripts:$PATH"
```

## Usage

### Interactive Menu (Recommended)

```bash
journal.py
```

Launches an interactive menu where you can:
- Create a weekly plan
- Create a daily journal entry
- Generate a weekly review
- Generate a monthly review

### Individual Scripts

You can also run scripts directly:

#### Weekly Planning (Sundays)

```bash
j-plan.py
```

Pulls from last week and prompts you for:
- Mindful eating intentions
- Focus areas

If a weekly plan already exists, you'll be prompted to:
- **(e)dit** - Open the existing file in your editor
- **(r)ecreate** - Delete and create a new plan from scratch
- **(q)uit** - Cancel and exit 

#### Daily Journal

```bash
j-daily.py
```

Creates a daily entry that:
- Prompts you for how many hours you slept
- Prompts you to reflect on mindful eating habits from the previous day
- Shows your focus areas as reminders
- Opens default editor to create entry
- auto-tags entry based on emotions list and prompts user to add more

If a journal entry already exists, you'll be prompted to:
- **(e)dit** - Open the existing file in your editor
- **(r)ecreate** - Delete and create a new entry from scratch
- **(q)uit** - Cancel and exit

#### Weekly Review (Saturdays)

```bash
j-review.py
```

Aggregates the week's data:
- Sleep score average and daily breakdown
- Tag frequency and timeline
- Eating reflections
- Prompts user to reflect on how well focus areas went

If a weekly review already exists, you'll be prompted to:
- **(e)dit** - Open the existing file in your editor
- **(r)ecreate** - Delete and create a new review from scratch
- **(q)uit** - Cancel and exit

#### Monthly Review (End of Month)

```bash
j-monthly.py
```

Aggregates data from the entire month:
- **Consistency metrics**: Count of daily entries, weekly plans, and weekly reviews
- **Sleep data**: Monthly average and trend compared to previous month
- **Emotional landscape**: Top 10 tags, new tags this month, tags that dropped off
- **Focus areas**: All unique focus areas from weekly plans
- **Eating intentions**: List of eating intentions from each week
- **Reflection prompts**: Month in one word and narrative summary (2-3 sentences)

If a monthly review already exists, you'll be prompted to:
- **(e)dit** - Open the existing file in your editor
- **(r)ecreate** - Delete and create a new review from scratch
- **(q)uit** - Cancel and exit

```

## Configuration

Edit `journal/config.py` to change:
- `JOURNAL_DIR` - where journal files are stored (default: `~/entries`)
- `EDITOR` - which editor to use (default: `$EDITOR` or `vim`)

## Roadmap

- [x] Monthly review script
- [ ] Sleep trend tracking (4-week rolling average)
- [ ] Migration tooling for existing journal files
