#!/bin/bash

# Weekly Review Script for Saturdays
JOURNAL_DIR="$HOME/Journal"
DATE=$(date +%Y-%m-%d)
FILE="$JOURNAL_DIR/review-$DATE.txt"

# Find this week's files
find_week_files() {
    local today=$(date +%s)
    local day_of_week=$(date +%u)
    
    # Calculate days since last Sunday
    if [ $day_of_week -eq 7 ]; then
        days_since_sunday=0
    else
        days_since_sunday=$day_of_week
    fi
    
    local sunday_date=$(date -d "$days_since_sunday days ago" +%Y-%m-%d)
    local weekly_file="$JOURNAL_DIR/weekly-$sunday_date.txt"
    
    # Find all daily files from this week
    local daily_files=()
    for i in $(seq 0 $((day_of_week-1))); do
        local day_date=$(date -d "$i days ago" +%Y-%m-%d)
        local daily_file="$JOURNAL_DIR/daily-$day_date.txt"
        if [ -f "$daily_file" ]; then
            daily_files+=("$daily_file")
        fi
    done
    
    echo "$weekly_file"
    printf '%s\n' "${daily_files[@]}"
}

# Calculate average sleep score
calculate_sleep_average() {
    local files=("$@")
    local total=0
    local count=0
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            local sleep=$(grep "^SLEEP QUALITY:" "$file" | sed 's/.*\[//' | sed 's/\].*//' | tr '[:upper:]' '[:lower:]')
            if [[ "$sleep" == *"good"* ]]; then
                total=$(echo "$total + 1" | bc)
                ((count++))
            elif [[ "$sleep" == *"decent"* ]]; then
                total=$(echo "$total + 0.5" | bc)
                ((count++))
            elif [[ "$sleep" == *"bad"* ]]; then
                total=$(echo "$total + 0" | bc)
                ((count++))
            fi
        fi
    done
    
    if [ $count -gt 0 ]; then
        echo "scale=2; $total / $count" | bc
    else
        echo "N/A"
    fi
}

# Get all eating reflections
get_eating_reflections() {
    local files=("$@")
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            local date=$(basename "$file" | sed 's/daily-//' | sed 's/.txt//')
            local reflection=$(sed -n '/^YESTERDAY'\''S EATING REFLECTION:/,/^TASKS COMPLETED/p' "$file" | grep -v "^YESTERDAY'S EATING" | grep -v "^TASKS COMPLETED" | grep -v "^$" | grep -v "^---" | grep -v "^===")
            if [ -n "$reflection" ]; then
                echo "[$date]"
                echo "$reflection"
                echo ""
            fi
        fi
    done
}

# Get all tags with timeline
get_tags_timeline() {
    local files=("$@")
    declare -A tag_days
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            local date=$(basename "$file" | sed 's/daily-//' | sed 's/.txt//')
            local day_name=$(date -d "$date" +%A)
            local tags=$(sed -n '/^TAGS:/,/^===/p' "$file" | grep -v "^TAGS:" | grep -v "^===" | grep -v "^$" | tr ' ' '\n' | tr ',' '\n' | sed 's/^[ \t]*//' | grep -v "^$")
            
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
    
    # Print tags with their timeline
    for tag in "${!tag_days[@]}"; do
        echo "$tag: ${tag_days[$tag]}"
    done | sort
}

# Get tag frequency
get_tag_frequency() {
    local files=("$@")
    declare -A tag_count
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            local tags=$(sed -n '/^TAGS:/,/^===/p' "$file" | grep -v "^TAGS:" | grep -v "^===" | grep -v "^$" | tr ' ' '\n' | tr ',' '\n' | sed 's/^[ \t]*//' | grep -v "^$")
            
            while IFS= read -r tag; do
                if [ -n "$tag" ]; then
                    ((tag_count[$tag]++))
                fi
            done <<< "$tags"
        fi
    done
    
    # Print frequency chart
    for tag in "${!tag_count[@]}"; do
        local count=${tag_count[$tag]}
        local bar=$(printf '█%.0s' $(seq 1 $count))
        echo "$tag ($count): $bar"
    done | sort -t'(' -k2 -rn
}

# Get completed vs incomplete tasks
get_task_status() {
    local weekly_file=$1
    
    if [ ! -f "$weekly_file" ]; then
        echo "No weekly plan found"
        return
    fi
    
    echo "COMPLETED TASKS:"
    echo "----------------"
    local completed=$(sed -n '/\[COMPLETED_TASKS\]/,/^===/p' "$weekly_file" | grep -v '^\[COMPLETED_TASKS\]' | grep -v '^===' | grep -v '^$')
    if [ -z "$completed" ]; then
        echo "(none)"
    else
        echo "$completed" | while read -r line; do echo "✓ $line"; done
    fi
    
    echo ""
    echo "INCOMPLETE TASKS:"
    echo "-----------------"
    
    # Get all tasks
    local all_tasks=$(sed -n '/^TASKS FOR THIS WEEK:/,/^FOCUS AREAS/p' "$weekly_file" | grep '^- ' | sed 's/^- //')
    
    # Filter out completed ones
    local has_incomplete=false
    while IFS= read -r task; do
        if [ -n "$task" ]; then
            if ! echo "$completed" | grep -Fq "$task"; then
                echo "○ $task"
                has_incomplete=true
            fi
        fi
    done <<< "$all_tasks"
    
    if [ "$has_incomplete" = false ]; then
        echo "(none - great job!)"
    fi
}

# Get focus areas
get_focus_areas() {
    local weekly_file=$1
    if [ ! -f "$weekly_file" ]; then
        echo "No weekly plan found"
        return
    fi
    
    sed -n '/^FOCUS AREAS/,/^===/p' "$weekly_file" | grep '^- '
}

# Main script
IFS=$'\n' read -d '' -r -a week_files < <(find_week_files)
WEEKLY_FILE="${week_files[0]}"
DAILY_FILES=("${week_files[@]:1}")

SLEEP_AVG=$(calculate_sleep_average "${DAILY_FILES[@]}")
EATING_REFLECTIONS=$(get_eating_reflections "${DAILY_FILES[@]}")
TAG_TIMELINE=$(get_tags_timeline "${DAILY_FILES[@]}")
TAG_FREQUENCY=$(get_tag_frequency "${DAILY_FILES[@]}")
TASK_STATUS=$(get_task_status "$WEEKLY_FILE")
FOCUS_AREAS=$(get_focus_areas "$WEEKLY_FILE")

# Create the review file
cat > "$FILE" << EOF
===========================================
WEEKLY REVIEW
Week ending: $(date +"%B %d, %Y")
===========================================

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
echo "Opening in default editor..."

${EDITOR:-vim} "$FILE"

echo "Weekly review complete!"
