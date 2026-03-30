#!/bin/bash
# Guard: analytics coverage reminder for mobile screens
# Spawns only when "if" matches: mobile-app .tsx files
# Replaces hookify rule: analytics-reminder
FILE_PATH=$(jq -r '.tool_input.file_path // ""')

if echo "$FILE_PATH" | grep -qE '/mobile-app/(app/.*\.tsx|src/features/.*/screens/.*\.tsx)$'; then
  jq -n '{
    decision: "block",
    reason: "Analytics check: does this screen/flow need analytics events? Check AnalyticsEvents.ts and consider running /analytics."
  }'
fi

exit 0
