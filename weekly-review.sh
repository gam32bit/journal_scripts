#!/bin/bash

# Weekly Review Script for Saturdays
# Aggregates data from daily journals and weekly plan

JOURNAL_DIR="$HOME/Journal"
DATE=$(date +%Y-%m-%d)
FILE="$JOURNAL_DIR/review-$DATE.txt"

# Create journal directory if it doesn't exist
mkdir -p "$JOURNAL_DIR"

# Find this week's Sunday and weekly file
find_weekly_file() {
    local day_of_week=$(date +%u)  # 1=Monday, 7=Sunday
    local days_since_sunday
    
    if [ "$day_of_week" -eq 7 ]; then
        days_since_sunday=0
    else
        days_since_sunday=$day_of_week
    fi
    
    local sunday_date=$(date -d "-${days_since_sunday} days" +%Y-%m-%d)
    local weekly_file="$JOURNAL_DIR/weekly-$sunday_date.txt"
    
    if [ -f "$weekly_file" ]; then
        echo "$weekly_file"
    else
        echo ""
    fi
}

# Find all daily files from this week (Sunday through today)
find_daily_files() {
    local day_of_week=$(date +%u)  # 1=Monday, 7=Sunday
    local days_since_sunday
    
    if [ "$day_of_week" -eq 7 ]; then
        days_since_sunday=0
    else
        days_since_sunday=$day_of_week
    fi
    
    # Collect daily files from Sunday to today
    for i in $(seq "$days_since_sunday" -1 0); do
        local day_date=$(date -d "-${i} days" +%Y-%m-%d)
        local daily_file="$JOURNAL_DIR/daily-$day_date.txt"
        if [ -f "$daily_file" ]; then
            echo "$daily_file"
        fi
    done
}

# Calculate average sleep score
calculate_sleep_average() {
    local total=0
    local count=0
    
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            local sleep=$(grep "^SLEEP QUALITY:" "$file" | sed 's/.*\[//' | sed 's/\].*//' | tr '[:upper:]' '[:lower:]')
            if [[ "$sleep" == *"good"* ]]; then
                total=$(echo "$total + 1" | bc)
                ((count++))
            elif [[ "$sleep" == *"decent"* ]]; then
                total=$(echo "$total + 0.5" | bc)
                ((count++))
            elif [[ "$sleep" == *"bad"* ]]; then
                ((count++))
            fi
        fi
    done
    
    if [ "$count" -gt 0 ]; then
        echo "scale=2; $total / $count" | bc
    else
        echo "N/A"
    fi
}

# Get all eating reflections
get_eating_reflections() {
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            local date=$(basename "$file" | sed 's/daily-//' | sed 's/.txt//')
            local reflection=$(sed -n "/^YESTERDAY'S EATING REFLECTION:/,/^TASKS COMPLETED/p" "$file" | \
                              grep -v "^YESTERDAY'S EATING" | \
                              grep -v "^TASKS COMPLETED" | \
                              grep -v '^$' | \
                              grep -v '^---' | \
                              grep -v '^===')
            if [ -n "$reflection" ]; then
                echo "[$date]"
                echo "$reflection"
                echo ""
            fi
        fi
    done
}

# Get tag frequency with bar chart
get_tag_frequency() {
    declare -A tag_count
    
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            local tags=$(sed -n '/^TAGS:/,/^===/p' "$file" | \
                        grep -v "^TAGS:" | \
                        grep -v "^===" | \
                        grep -v '^$' | \
                        tr ' ' '\n' | \
                        tr ',' '\n' | \
                        sed 's/^[ \t]*//' | \
                        grep -v '^$')
            
            while IFS= read -r tag; do
                if [ -n "$tag" ]; then
                    ((tag_count[$tag]++))
                fi
            done <<< "$tags"
        fi
    done
    
    if [ ${#tag_count[@]} -eq 0 ]; then
        echo "(No tags recorded)"
        return
    fi
    
    # Print frequency chart sorted by count
    for tag in "${!tag_count[@]}"; do
        local count=${tag_count[$tag]}
        local bar=$(printf '█%.0s' $(seq 1 "$count"))
        echo "$tag ($count): $bar"
    done | sort -t'(' -k2 -rn
}

# Get tags with timeline (which days they appeared)
get_tags_timeline() {
    declare -A tag_days
    
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            local date=$(basename "$file" | sed 's/daily-//' | sed 's/.txt//')
            local day_name=$(date -d "$date" +%A)
            local tags=$(sed -n '/^TAGS:/,/^===/p' "$file" | \
                        grep -v "^TAGS:" | \
                        grep -v "^===" | \
                        grep -v '^$' | \
                        tr ' ' '\n' | \
                        tr ',' '\n' | \
                        sed 's/^[ \t]*//' | \
                        grep -v '^$')
            
            while IFS= read -r tag; do
                if [ -n "$tag" ]; then
                    if [ -z "${tag_days[$tag]}" ]; then
                        tag_days[$tag]="$day_name"
                    else
                        tag_days[$tag]="${tag_days[$tag]}, $day_name"
                    fi
                fi
            done <<< "$tags"
        fi
    done
    
    if [ ${#tag_days[@]} -eq 0 ]; then
        echo "(No tags recorded)"
        return
    fi
    
    # Print tags with their timeline
    for tag in "${!tag_days[@]}"; do
        echo "$tag: ${tag_days[$tag]}"
    done | sort
}

# Get completed vs incomplete tasks
get_task_status() {
    local weekly_file="$1"
    
    if [ -z "$weekly_file" ] || [ ! -f "$weekly_file" ]; then
        echo "No weekly plan found"
        return
    fi
    
    echo "COMPLETED:"
    local completed=$(sed -n '/\[COMPLETED_TASKS\]/,/^===/p' "$weekly_file" | \
                     grep -v '^\[COMPLETED_TASKS\]' | \
                     grep -v '^===' | \
                     grep -v '^$')
    
    if [ -z "$completed" ]; then
        echo "  (none)"
    else
        echo "$completed" | while read -r line; do
            if [ -n "$line" ]; then
                echo "  ✓ $line"
            fi
        done
    fi
    
    echo ""
    echo "INCOMPLETE:"
    
    # Get all tasks
    local all_tasks=$(sed -n '/^TASKS FOR THIS WEEK:/,/^FOCUS AREAS/p' "$weekly_file" | \
                     grep '^- ' | \
                     sed 's/^- //')
    
    # Filter out completed ones
    local has_incomplete=false
    while IFS= read -r task; do
        if [ -n "$task" ]; then
            if ! echo "$completed" | grep -Fxq "$task"; then
                echo "  ○ $task"
                has_incomplete=true
            fi
        fi
    done <<< "$all_tasks"
    
    if [ "$has_incomplete" = false ]; then
        echo "  (none - great job!)"
    fi
}

# Get focus areas from weekly plan
get_focus_areas() {
    local weekly_file="$1"
    
    if [ -z "$weekly_file" ] || [ ! -f "$weekly_file" ]; then
        echo "(No weekly plan found)"
        return
    fi
    
    local areas=$(sed -n '/^FOCUS AREAS/,/^\(\[COMPLETED_TASKS\]\|===\)/p' "$weekly_file" | \
                 grep '^- ')
    
    if [ -n "$areas" ]; then
        echo "$areas"
    else
        echo "(No focus areas defined)"
    fi
}

# Check if review already exists
if [ -f "$FILE" ]; then
    echo "Weekly review already exists: $FILE"
    echo "Opening existing file..."
    vim "$FILE"
    exit 0
fi

# Gather data
WEEKLY_FILE=$(find_weekly_file)
DAILY_FILES=$(find_daily_files)

# Calculate metrics by piping daily files to functions
SLEEP_AVG=$(echo "$DAILY_FILES" | calculate_sleep_average)
EATING_REFLECTIONS=$(echo "$DAILY_FILES" | get_eating_reflections)
TAG_FREQUENCY=$(echo "$DAILY_FILES" | get_tag_frequency)
TAG_TIMELINE=$(echo "$DAILY_FILES" | get_tags_timeline)
TASK_STATUS=$(get_task_status "$WEEKLY_FILE")
FOCUS_AREAS=$(get_focus_areas "$WEEKLY_FILE")

# Count daily entries found
DAILY_COUNT=$(echo "$DAILY_FILES" | grep -c .)

# Create the review file
cat > "$FILE" << EOF
===========================================
WEEKLY REVIEW
Week ending: $(date +"%B %d, %Y")
===========================================

Daily entries found: $DAILY_COUNT

SLEEP ANALYSIS:
---------------
Average Sleep Score: $SLEEP_AVG
(Good=1.0, Decent=0.5, Bad=0.0)

===========================================

EMOTIONAL LANDSCAPE (Tags):
----------------------------

TAG FREQUENCY:
$TAG_FREQUENCY

TAG TIMELINE:
$TAG_TIMELINE

===========================================

EATING REFLECTIONS:
-------------------
$EATING_REFLECTIONS

===========================================

TASK COMPLETION:
----------------
$TASK_STATUS

===========================================

FOCUS AREAS THIS WEEK:
----------------------
$FOCUS_AREAS

===========================================

WEEKLY REFLECTION:
------------------

How did you do with your focus areas this week?


What went well this week?


What could be improved?


Key insights or lessons learned:


===========================================
EOF

echo "Weekly review created: $FILE"
echo "Opening in vim..."

vim "$FILE"

echo "Weekly review complete!"
