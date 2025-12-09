#!/bin/bash
# Daily Journal Script
# Creates daily journal entries with tasks pulled from weekly plan

JOURNAL_DIR="$HOME/Journal"
DATE=$(date +%Y-%m-%d)
FILE="$JOURNAL_DIR/daily-$DATE.txt"

# Create journal directory if it doesn't exist
mkdir -p "$JOURNAL_DIR"

# Find the most recent weekly plan (from this week's Sunday)
find_weekly_file() {
    local day_of_week=$(date +%u)  # 1=Monday, 7=Sunday
    local days_since_sunday
    
    # Calculate days since last Sunday
    if [ "$day_of_week" -eq 7 ]; then
        days_since_sunday=0
    else
        days_since_sunday=$day_of_week
    fi
    
    # Get last Sunday's date
    local sunday_date=$(date -d "-${days_since_sunday} days" +%Y-%m-%d)
    local weekly_file="$JOURNAL_DIR/weekly-$sunday_date.txt"
    
    if [ -f "$weekly_file" ]; then
        echo "$weekly_file"
    else
        echo ""
    fi
}

# Extract uncompleted tasks from weekly file
get_remaining_tasks() {
    local weekly_file="$1"
    if [ -z "$weekly_file" ] || [ ! -f "$weekly_file" ]; then
        echo "No weekly plan found"
        return
    fi
    
    # Get completed tasks (between [COMPLETED_TASKS] and end of file or next section)
    local completed=$(sed -n '/\[COMPLETED_TASKS\]/,/^===/p' "$weekly_file" | \
                      grep -v '^\[COMPLETED_TASKS\]' | \
                      grep -v '^===' | \
                      grep -v '^$')
    
    # Get all tasks (between TASKS FOR THIS WEEK and FOCUS AREAS)
    local all_tasks=$(sed -n '/^TASKS FOR THIS WEEK:/,/^FOCUS AREAS/p' "$weekly_file" | \
                      grep '^- ' | \
                      sed 's/^- //')
    
    # Filter out completed ones
    local found_any=false
    while IFS= read -r task; do
        if [ -n "$task" ]; then
            if ! echo "$completed" | grep -Fxq "$task"; then
                echo "- $task"
                found_any=true
            fi
        fi
    done <<< "$all_tasks"
    
    if [ "$found_any" = false ]; then
        echo "(All tasks completed or none defined)"
    fi
}

# Extract focus areas from weekly file
get_focus_areas() {
    local weekly_file="$1"
    if [ -z "$weekly_file" ] || [ ! -f "$weekly_file" ]; then
        echo "No weekly plan found"
        return
    fi
    
    # Extract between FOCUS AREAS and the next === or [COMPLETED_TASKS]
    local areas=$(sed -n '/^FOCUS AREAS/,/^\(\[COMPLETED_TASKS\]\|===\)/p' "$weekly_file" | \
                  grep '^- ')
    
    if [ -n "$areas" ]; then
        echo "$areas"
    else
        echo "(No focus areas defined)"
    fi
}

# Check if today's file already exists
if [ -f "$FILE" ]; then
    echo "Today's journal already exists: $FILE"
    echo "Opening existing file..."
    vim "$FILE"
    exit 0
fi

# Gather data from weekly file
WEEKLY_FILE=$(find_weekly_file)
REMAINING_TASKS=$(get_remaining_tasks "$WEEKLY_FILE")
FOCUS_AREAS=$(get_focus_areas "$WEEKLY_FILE")

# Create daily journal template
cat > "$FILE" << EOF
===========================================
DAILY JOURNAL
Date: $(date +"%A, %B %d, %Y")
===========================================

WEEKLY TASKS REMAINING:
-----------------------
$REMAINING_TASKS

FOCUS AREAS:
------------
$FOCUS_AREAS

===========================================

SLEEP QUALITY: [Good/Decent/Bad]

YESTERDAY'S EATING REFLECTION:


TASKS COMPLETED YESTERDAY:
--------------------------
- 

===========================================

JOURNAL ENTRY:
--------------


===========================================

TAGS:

===========================================
[WEEKLY_FILE:$WEEKLY_FILE]
EOF

echo "Daily journal created: $FILE"
echo "Opening in vim..."

# Open in vim
vim "$FILE"

# After editing, process completed tasks
echo ""
echo "Processing completed tasks..."

# Extract completed tasks from the daily entry
# Gets lines starting with "- " after the TASKS COMPLETED YESTERDAY section
COMPLETED_TODAY=$(sed -n '/^TASKS COMPLETED YESTERDAY:/,/^===/p' "$FILE" | \
                  grep '^- ' | \
                  sed 's/^- //' | \
                  grep -v '^$')

if [ -n "$COMPLETED_TODAY" ] && [ -n "$WEEKLY_FILE" ] && [ -f "$WEEKLY_FILE" ]; then
    while IFS= read -r task; do
        if [ -n "$task" ]; then
            # Check if task isn't already in completed section
            if ! grep -Fxq "$task" <(sed -n '/\[COMPLETED_TASKS\]/,/^===/p' "$WEEKLY_FILE"); then
                # Add to completed section (after [COMPLETED_TASKS] line)
                sed -i "/\[COMPLETED_TASKS\]/a $task" "$WEEKLY_FILE"
                echo "✓ Marked complete: $task"
            else
                echo "  Already marked: $task"
            fi
        fi
    done <<< "$COMPLETED_TODAY"
else
    echo "No tasks to mark complete."
fi

echo ""
echo "Journal entry saved!"
