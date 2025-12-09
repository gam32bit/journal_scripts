#!/bin/bash
# Weekly Planning Script for Sundays
# Creates weekly plan template with tasks and focus areas

JOURNAL_DIR="$HOME/Journal"
DATE=$(date +%Y-%m-%d)
FILE="$JOURNAL_DIR/weekly-$DATE.txt"

# Create journal directory if it doesn't exist
mkdir -p "$JOURNAL_DIR"

# Check if this week's plan already exists
if [ -f "$FILE" ]; then
    echo "Weekly plan already exists: $FILE"
    echo "Opening existing file..."
    vim "$FILE"
    exit 0
fi

# Create the weekly planning template
# Using unquoted EOF so variables expand directly
cat > "$FILE" << EOF
===========================================
WEEKLY PLAN
Week of: $(date +"%B %d, %Y")
===========================================

TASKS FOR THIS WEEK:
--------------------
- 
- 
- 
- 
- 

FOCUS AREAS (Mood/Habits):
--------------------------
- 
- 

===========================================
[COMPLETED_TASKS]

===========================================
EOF

echo "Weekly plan created: $FILE"
echo "Opening in vim..."

# Open in vim
vim "$FILE"

echo "Weekly plan saved!"
