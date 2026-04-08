#!/bin/bash
# Analytics Reminder — Prompt to add analytics events for new screens/pages.
#
# Event:     PostToolUse
# Matcher:   Write|Edit
# Blocking:  Soft (outputs a reminder, does not exit 2)
# Wired:     No (project-specific — configure SCREEN_FILE_PATTERN for your app)
#
# When editing files that match the screen pattern, outputs a reminder to
# check analytics coverage.
#
# Configuration:
#   SCREEN_FILE_PATTERN  — regex matching screen/page files that need analytics
#   REMINDER_MESSAGE     — the reminder text to display
#
# To enable, add to .claude/settings.json hooks.PostToolUse:
#   {
#     "matcher": "Write|Edit",
#     "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/guards/analytics-reminder.sh"}]
#   }

# === CONFIGURE FOR YOUR PROJECT ===
SCREEN_FILE_PATTERN="/mobile-app/(app/.*\.tsx|src/features/.*/screens/.*\.tsx)$"
REMINDER_MESSAGE="Analytics check: does this screen/flow need analytics events? Check your analytics config and consider tracking key user actions."

# --- Read file path from stdin ---
FILE_PATH=$(jq -r '.tool_input.file_path // ""')

if echo "$FILE_PATH" | grep -qE "$SCREEN_FILE_PATTERN"; then
  jq -n --arg msg "$REMINDER_MESSAGE" '{
    decision: "block",
    reason: $msg
  }'
fi

exit 0
