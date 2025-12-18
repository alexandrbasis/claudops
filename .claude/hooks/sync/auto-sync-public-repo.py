#!/usr/bin/env python3
"""
Auto-sync Claude Code configuration to public repository
Triggers on PostToolUse for git commit commands
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def log(message: str, log_file: Path):
    """Log message to file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] [auto-sync-public] {message}\n")


def get_changed_files_in_last_commit() -> list[str]:
    """Get list of files changed in the last commit"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError as e:
        # Might fail on initial commit or if HEAD~1 doesn't exist
        # Try alternative approach
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            return []


def has_claude_changes(files: list[str]) -> bool:
    """Check if any .claude/ files were changed"""
    return any(f.startswith('.claude/') for f in files if f)


def trigger_sync(project_dir: Path, log_file: Path):
    """Trigger the sync script"""
    script_path = project_dir / ".claude" / "scripts" / "sync-to-public.sh"

    if not script_path.exists():
        log(f"Sync script not found: {script_path}", log_file)
        return False

    # Get public repo path from environment
    public_repo_path = os.getenv(
        "PUBLIC_REPO_PATH",
        str(project_dir / "wythm-claude-workflows")
    )

    log(f"Triggering sync to {public_repo_path}", log_file)

    try:
        # Run sync script in background to not block Claude
        env = os.environ.copy()
        env["PUBLIC_REPO_PATH"] = public_repo_path

        result = subprocess.run(
            [str(script_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )

        if result.returncode == 0:
            log("Sync completed successfully", log_file)
            # Extract and log the GitHub URL from output
            for line in result.stdout.split('\n'):
                if 'github.com' in line:
                    log(f"Updated: {line.strip()}", log_file)
            return True
        else:
            log(f"Sync failed with code {result.returncode}", log_file)
            log(f"Error: {result.stderr}", log_file)
            return False

    except subprocess.TimeoutExpired:
        log("Sync script timed out after 60 seconds", log_file)
        return False
    except Exception as e:
        log(f"Error running sync script: {str(e)}", log_file)
        return False


def main():
    """Main hook logic"""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)

        # Extract relevant fields
        hook_event = input_data.get("hook_event_name", "")
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        cwd = input_data.get("cwd", "")

        # Setup paths
        project_dir = Path(cwd) if cwd else Path.cwd()
        log_file = project_dir / ".claude" / "hooks" / "logs" / "hook-debug.log"

        # Log hook activation
        log(f"Hook triggered: {hook_event} for {tool_name}", log_file)

        # Only process PostToolUse events for Bash commands
        if hook_event != "PostToolUse" or tool_name != "Bash":
            sys.exit(0)

        # Check if this is a git commit command
        command = tool_input.get("command", "")
        if "git commit" not in command:
            sys.exit(0)

        log(f"Git commit detected: {command[:100]}", log_file)

        # Check if .claude/ files were changed
        changed_files = get_changed_files_in_last_commit()

        if not changed_files:
            log("No changed files detected", log_file)
            sys.exit(0)

        log(f"Files changed: {len(changed_files)}", log_file)

        if has_claude_changes(changed_files):
            claude_files = [f for f in changed_files if f.startswith('.claude/')]
            log(f"Claude files changed: {', '.join(claude_files[:5])}", log_file)

            # Trigger sync
            success = trigger_sync(project_dir, log_file)

            if not success:
                log("Sync failed but not blocking commit", log_file)

        else:
            log("No .claude/ files changed, skipping sync", log_file)

        # Always return success (exit 0) - don't block commits even if sync fails
        sys.exit(0)

    except Exception as e:
        # Log error but don't block
        try:
            project_dir = Path.cwd()
            log_file = project_dir / ".claude" / "hooks" / "logs" / "hook-debug.log"
            log(f"Unexpected error: {str(e)}", log_file)
        except:
            pass

        # Exit successfully to not block Claude
        sys.exit(0)


if __name__ == "__main__":
    main()
