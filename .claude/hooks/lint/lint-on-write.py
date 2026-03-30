#!/usr/bin/env python3
"""
PostToolUse hook for automatic formatting of TypeScript files.

Runs after Write/Edit operations on TypeScript files in backend/ or mobile-app/.
Auto-formats with Prettier (non-blocking).

Exit codes:
- 0: Success or not applicable (always non-blocking)
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


def is_typescript_file(file_path: str) -> bool:
    """Check if file is a TypeScript source file."""
    return file_path.endswith((".ts", ".tsx"))


def get_target_dir(file_path: str, project_dir: str) -> Optional[str]:
    """Return the target directory (backend/ or mobile-app/) if file is inside one."""
    file_abs = Path(file_path).resolve()

    for subdir in ("backend", "mobile-app"):
        target = Path(project_dir) / subdir
        try:
            file_abs.relative_to(target)
            return str(target)
        except ValueError:
            continue

    return None


def should_process_file(file_path: str, project_dir: str) -> Tuple[bool, Optional[str]]:
    """Determine if file should be formatted. Returns (should_process, target_dir)."""
    if not is_typescript_file(file_path):
        return False, None

    target_dir = get_target_dir(file_path, project_dir)
    if not target_dir:
        return False, None

    # Skip generated files
    if any(skip in file_path for skip in (
        "node_modules", ".generated.", "prisma/migrations", "dist/"
    )):
        return False, None

    return True, target_dir


def format_file(file_path: str, cwd: str) -> Tuple[bool, str]:
    """Auto-format file with Prettier. Returns (success, message)."""
    try:
        result = subprocess.run(
            ["npx", "prettier", "--write", file_path],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=15
        )

        file_name = Path(file_path).name
        if result.returncode == 0:
            return True, f"prettier: formatted {file_name}"
        else:
            err = result.stderr.strip()[:200]
            return False, f"prettier: failed on {file_name} — {err}"

    except subprocess.TimeoutExpired:
        return False, "prettier: timed out (15s)"
    except FileNotFoundError:
        return False, "prettier: not found (npx not available)"
    except Exception as e:
        return False, f"prettier: error — {e}"


def main() -> None:
    """Main hook execution."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", input_data.get("cwd", os.getcwd()))

    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    should_process, target_dir = should_process_file(file_path, project_dir)
    if not should_process:
        sys.exit(0)

    if not Path(file_path).exists():
        sys.exit(0)

    success, msg = format_file(file_path, target_dir)
    print(f"{'✓' if success else '✗'} {msg}", file=sys.stderr)

    # Always non-blocking
    sys.exit(0)


if __name__ == "__main__":
    main()
