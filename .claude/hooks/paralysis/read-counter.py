#!/usr/bin/env python3
"""
Analysis Paralysis Guard — PostToolUse hook.

Tracks consecutive read-only tool calls (Read, Grep, Glob) without any
write action (Write, Edit, Bash) in between. After 5+ consecutive reads,
injects a warning into the system message telling the agent to stop
exploring and start writing code.

State is persisted to .claude/hooks/logs/.read-streak.json so it
survives across hook invocations within a session.
"""

import json
import os
import sys
import time

# --- Configuration ---
STREAK_THRESHOLD = 5
STATE_FILENAME = ".read-streak.json"
# Stale after 30 minutes (new session likely started)
STALE_TIMEOUT_S = 30 * 60

READ_TOOLS = {"Read", "Grep", "Glob"}
WRITE_TOOLS = {"Write", "Edit", "Bash", "MultiEdit", "NotebookEdit"}

WARNING_MESSAGE = """PARALYSIS GUARD: You've made {streak}+ read-only calls without writing anything.
STOP exploring. You likely have enough context. Either:
1. Write code now (tests or implementation)
2. State what's blocking you and ask the user for clarification
The task document is the source of truth — do not endlessly explore the codebase."""


def get_state_path() -> str:
    """Resolve the state file path relative to the project's hooks/logs dir."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir:
        logs_dir = os.path.join(project_dir, ".claude", "hooks", "logs")
    else:
        # Fallback: relative to this script
        logs_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    return os.path.join(logs_dir, STATE_FILENAME)


def load_state(path: str) -> dict:
    """Load streak state, resetting if stale or missing."""
    try:
        with open(path, "r") as f:
            state = json.load(f)
        # Reset if stale (e.g., new session)
        if time.time() - state.get("last_update", 0) > STALE_TIMEOUT_S:
            return {"streak": 0, "last_update": time.time()}
        return state
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {"streak": 0, "last_update": time.time()}


def save_state(path: str, state: dict) -> None:
    """Persist streak state."""
    state["last_update"] = time.time()
    with open(path, "w") as f:
        json.dump(state, f)


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        # Can't parse input — pass through
        print(json.dumps({}))
        return

    tool_name = input_data.get("tool_name", "")

    state_path = get_state_path()
    state = load_state(state_path)

    if tool_name in READ_TOOLS:
        state["streak"] = state.get("streak", 0) + 1
    elif tool_name in WRITE_TOOLS:
        # Reset streak on any write action
        state["streak"] = 0
    # Other tools (e.g., Agent, AskUserQuestion) don't affect the streak

    save_state(state_path, state)

    streak = state.get("streak", 0)
    if streak >= STREAK_THRESHOLD:
        # Emit warning but allow the tool to proceed
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": WARNING_MESSAGE.format(streak=streak)
            }
        }
        print(json.dumps(result))
    else:
        # No warning — empty response means "proceed normally"
        print(json.dumps({}))


if __name__ == "__main__":
    main()
