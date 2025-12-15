# Journal Scripts

> ⚠️ **Work in Progress** - This system is actively being developed and may change.

A Python-based personal productivity system for weekly planning, daily journaling, and reflection.

## Overview

This system connects weekly intentions with daily practice through four scripts:

| Script | Purpose | When to use |
|--------|---------|-------------|
| `j-plan.py` | Create weekly plan with tasks, focus areas, and writing prompts | Sunday |
| `j-daily.py` | Daily journal with tasks pulled from weekly plan | Daily |
| `j-prompt.py` | Daily writing entry with prompts from weekly plan | As needed |
| `j-review.py` | Aggregate the week's data into a review document | Saturday |

## File Structure

Journal entries are stored in `~/Journal/` organized by year and month:

```
~/Journal/
└── 2025/
    └── 12/
        ├── weekly-2025-12-14.md
        ├── daily-2025-12-15.md
        ├── daily-2025-12-16.md
        ├── prompt-2025-12-15.md
        └── review-2025-12-20.md
```

## Installation

```bash
# Clone the repo
git clone git@github.com:gam32bit/journal_scripts.git ~/scripts

# Make entry points executable
chmod +x ~/scripts/j-*.py

# Add to PATH (add to ~/.bashrc)
export PATH="$HOME/scripts:$PATH"
```

## Usage

### Weekly Planning (Sundays)

```bash
j-plan.py
```

Creates a template with:
- Tasks for the week (checkbox format)
- Focus areas (mood/habits to track)
- Writing prompts

### Daily Journal

```bash
j-daily.py
```

Creates a daily entry that:
- Pulls incomplete tasks from your weekly plan
- Shows your focus areas as reminders
- Tracks sleep (O/−/X) and eating reflections
- Syncs completed tasks back to weekly plan when you save

### Daily Writing Prompt

```bash
j-prompt.py
```

Creates a writing entry with:
- Available prompts from your weekly plan
- Space to select today's prompt and write

### Weekly Review (Saturdays)

```bash
j-review.py
```

Aggregates the week's data:
- Sleep score average and daily breakdown
- Tag frequency and timeline
- Eating reflections
- Writing excerpts
- Task completion status
- Reflection prompts

## Format Reference

### Tags
```
## Tags: work, sleep, anxiety
```

### Sleep Score
```
## Sleep quality: O
```
- `O` = Good (1.0)
- `-` = Decent (0.5)
- `X` = Bad (0.0)

### Task Completion
Mark tasks complete in your daily journal by changing `[ ]` to `[x]`:
```
## Weekly tasks remaining:
- [x] Finish project proposal
- [ ] Call mom
```

## Configuration

Edit `journal/config.py` to change:
- `JOURNAL_DIR` - where journal files are stored (default: `~/Journal`)
- `EDITOR` - which editor to use (default: `$EDITOR` or `vim`)

## Roadmap

- [ ] Monthly review script
- [ ] Sleep trend tracking (4-week rolling average)
- [ ] Migration tooling for existing journal files
