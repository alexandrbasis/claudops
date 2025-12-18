#!/usr/bin/env python3
"""
PostToolUse hook for automatic linting and formatting of Python files.

This hook runs after Write/Edit operations on Python files in content-intelligence/.
It automatically formats code with black and isort, then runs flake8 and mypy.

Features:
- Automatic formatting (black + isort) with fixes
- Fast scope: only checks modified file, not entire project
- Smart detection: only runs on Python files in content-intelligence/
- Error feedback: provides actionable feedback to Claude if issues found

Exit codes:
- 0: Success (all checks passed or auto-fixed)
- 2: Blocking error (shows stderr to Claude for auto-fix)
- 1: Non-blocking error (shows to user only)
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def is_python_file(file_path: str) -> bool:
    """Check if file is a Python source file."""
    return file_path.endswith(".py")


def is_in_content_intelligence(file_path: str, project_dir: str) -> bool:
    """Check if file is inside content-intelligence/ directory."""
    file_path_abs = Path(file_path).resolve()
    content_intelligence_dir = Path(project_dir) / "content-intelligence"

    try:
        # Check if file is relative to content-intelligence/
        file_path_abs.relative_to(content_intelligence_dir)
        return True
    except ValueError:
        return False


def should_process_file(file_path: str, project_dir: str) -> bool:
    """Determine if file should be linted."""
    # Skip non-Python files
    if not is_python_file(file_path):
        return False

    # Skip files outside content-intelligence/
    if not is_in_content_intelligence(file_path, project_dir):
        return False

    # Skip virtual environment files
    if "venv" in file_path or ".venv" in file_path:
        return False

    # Skip migrations (they're auto-generated)
    if "/alembic/versions/" in file_path:
        return False

    return True


def run_command(cmd: List[str], cwd: str) -> Tuple[int, str, str]:
    """Execute a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out after 30 seconds"
    except Exception as e:
        return 1, "", f"Failed to execute command: {e}"


def get_venv_tool_path(tool_name: str, project_dir: str) -> str:
    """Get path to tool in virtual environment."""
    content_intelligence_dir = Path(project_dir) / "content-intelligence"
    venv_tool = content_intelligence_dir / ".venv" / "bin" / tool_name

    # Return venv tool if it exists, otherwise use global
    return str(venv_tool) if venv_tool.exists() else tool_name


def format_file(file_path: str, project_dir: str) -> Tuple[bool, str]:
    """
    Auto-format file with black and isort.

    Returns:
        (success, message) tuple
    """
    content_intelligence_dir = str(Path(project_dir) / "content-intelligence")
    messages = []

    # Run black
    black_cmd = get_venv_tool_path("black", project_dir)
    returncode, stdout, stderr = run_command(
        [black_cmd, file_path],
        cwd=content_intelligence_dir
    )

    if returncode == 0:
        if "reformatted" in stdout:
            messages.append(f"✓ black: reformatted {Path(file_path).name}")
        else:
            messages.append(f"✓ black: already formatted")
    else:
        messages.append(f"✗ black: {stderr}")
        return False, "\n".join(messages)

    # Run isort
    isort_cmd = get_venv_tool_path("isort", project_dir)
    returncode, stdout, stderr = run_command(
        [isort_cmd, file_path],
        cwd=content_intelligence_dir
    )

    if returncode == 0:
        if "Fixing" in stderr or "Fixing" in stdout:
            messages.append(f"✓ isort: fixed imports")
        else:
            messages.append(f"✓ isort: imports already sorted")
    else:
        messages.append(f"✗ isort: {stderr}")
        return False, "\n".join(messages)

    return True, "\n".join(messages)


def check_flake8(file_path: str, project_dir: str) -> Tuple[bool, str]:
    """
    Run flake8 on file.

    Returns:
        (success, message) tuple
    """
    content_intelligence_dir = str(Path(project_dir) / "content-intelligence")

    flake8_cmd = get_venv_tool_path("flake8", project_dir)
    returncode, stdout, stderr = run_command(
        [flake8_cmd, file_path],
        cwd=content_intelligence_dir
    )

    if returncode == 0:
        return True, "✓ flake8: no style violations"
    else:
        # flake8 outputs violations to stdout
        violations = stdout.strip() if stdout.strip() else stderr.strip()
        return False, f"✗ flake8: found style violations\n{violations}"


def check_mypy(file_path: str, project_dir: str) -> Tuple[bool, str]:
    """
    Run mypy on file.

    Returns:
        (success, message) tuple
    """
    content_intelligence_dir = str(Path(project_dir) / "content-intelligence")

    # Get relative path for mypy (it expects paths relative to project root)
    try:
        file_path_abs = Path(file_path).resolve()
        rel_path = file_path_abs.relative_to(Path(content_intelligence_dir))

        mypy_cmd = get_venv_tool_path("mypy", project_dir)
        returncode, stdout, stderr = run_command(
            [mypy_cmd, str(rel_path), "--no-error-summary"],
            cwd=content_intelligence_dir
        )

        if returncode == 0:
            return True, "✓ mypy: type checks passed"
        else:
            errors = stdout.strip() if stdout.strip() else stderr.strip()
            # Filter out "Success: no issues found" false positives
            if "Success: no issues found" in errors:
                return True, "✓ mypy: type checks passed"
            return False, f"✗ mypy: found type errors\n{errors}"
    except ValueError:
        # File is not in content-intelligence/ directory
        return True, "⊘ mypy: skipped (file outside content-intelligence/)"


def main() -> None:
    """Main hook execution."""
    # Load input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract hook data
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", input_data.get("cwd", os.getcwd()))

    # Only process Write/Edit operations
    if tool_name not in ["Write", "Edit"]:
        sys.exit(0)

    # Get file path
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Check if we should process this file
    if not should_process_file(file_path, project_dir):
        sys.exit(0)

    # Verify file exists (it should, since PostToolUse runs after write)
    if not Path(file_path).exists():
        print(f"Warning: File does not exist: {file_path}", file=sys.stderr)
        sys.exit(0)

    file_name = Path(file_path).name
    print(f"\n🔍 Linting {file_name}...", file=sys.stderr)

    # Step 1: Auto-format
    format_success, format_msg = format_file(file_path, project_dir)
    print(format_msg, file=sys.stderr)

    if not format_success:
        print("\n❌ Formatting failed. Please check the file manually.", file=sys.stderr)
        sys.exit(2)  # Blocking error - shows to Claude

    # Step 2: Check flake8
    flake8_success, flake8_msg = check_flake8(file_path, project_dir)
    print(flake8_msg, file=sys.stderr)

    # Step 3: Check mypy (only if file is in app/ directory - strict typing)
    mypy_success = True
    mypy_msg = ""

    if "/app/" in file_path or file_path.endswith("/app"):
        mypy_success, mypy_msg = check_mypy(file_path, project_dir)
        print(mypy_msg, file=sys.stderr)

    # Determine overall result
    if flake8_success and mypy_success:
        print(f"\n✅ All checks passed for {file_name}", file=sys.stderr)
        sys.exit(0)
    else:
        error_summary = []
        if not flake8_success:
            error_summary.append("flake8 violations")
        if not mypy_success:
            error_summary.append("mypy type errors")

        print(f"\n❌ Found issues: {', '.join(error_summary)}", file=sys.stderr)
        print("\nPlease fix these issues before proceeding.", file=sys.stderr)
        sys.exit(2)  # Blocking error - shows to Claude for auto-fix


if __name__ == "__main__":
    main()
