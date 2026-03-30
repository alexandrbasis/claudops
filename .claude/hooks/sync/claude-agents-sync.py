#!/usr/bin/env python3
"""
Claude/Agents Files Synchronization Hook

This hook ensures that CLAUDE.md and AGENTS.md files stay synchronized across the entire project.
When changes are detected in either file, the corresponding counterpart is updated automatically.

File pairs to synchronize:
1. Root: CLAUDE.md ↔ AGENTS.md
2. Backend: backend/CLAUDE.md ↔ backend/AGENTS.md
3. Mobile App: mobile-app/CLAUDE.md ↔ mobile-app/AGENTS.md
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

def log_message(message, level="INFO"):
    """Log messages with timestamp to stderr (stdout is reserved for hook JSON output)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}", file=sys.stderr)
    sys.stderr.flush()

def calculate_file_hash(file_path):
    """Calculate MD5 hash of file content"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None

def get_file_pairs(base_path):
    """Define the file pairs that should be synchronized"""
    base_path = Path(base_path).resolve()

    # Find repository root (directory that contains ".claude/")
    project_root = None
    for candidate in [base_path] + list(base_path.parents):
        if (candidate / ".claude").exists():
            project_root = candidate
            break

    # Fallback (shouldn't normally happen)
    if project_root is None:
        project_root = Path.cwd().resolve()

    def resolve_existing_path(*candidates: Path) -> Path:
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]

    root_claude = resolve_existing_path(project_root / "CLAUDE.md", project_root / "claude.md")
    root_agents = resolve_existing_path(project_root / "AGENTS.md", project_root / "agents.md")
    backend_claude = resolve_existing_path(
        project_root / "backend" / "CLAUDE.md",
        project_root / "backend" / "claude.md",
    )
    backend_agents = resolve_existing_path(
        project_root / "backend" / "AGENTS.md",
        project_root / "backend" / "agents.md",
    )
    mobile_claude = resolve_existing_path(
        project_root / "mobile-app" / "CLAUDE.md",
        project_root / "mobile-app" / "claude.md",
    )
    mobile_agents = resolve_existing_path(
        project_root / "mobile-app" / "AGENTS.md",
        project_root / "mobile-app" / "agents.md",
    )

    return [
        {
            "source": root_claude,
            "target": root_agents,
            "name": "Root"
        },
        {
            "source": backend_claude,
            "target": backend_agents,
            "name": "Backend"
        },
        {
            "source": mobile_claude,
            "target": mobile_agents,
            "name": "Mobile App"
        }
    ]

def should_sync_file(file_path):
    """Check if a file should trigger synchronization"""
    file_path = Path(file_path)
    filename = file_path.name.lower()

    # Check if this is CLAUDE.md or AGENTS.md file
    return filename in ["claude.md", "agents.md"]

def find_pair_for_file(changed_file, file_pairs):
    """Find the corresponding pair for a changed file"""
    changed_path = Path(changed_file).resolve()

    def is_same_file(a: Path, b: Path) -> bool:
        """
        Robust file identity check across case-insensitive filesystems (macOS)
        and case-sensitive ones (Linux/CI).
        """
        try:
            if a.exists() and b.exists():
                return a.samefile(b)
        except Exception:
            pass
        return a.resolve() == b.resolve()

    for pair in file_pairs:
        source_path = Path(pair["source"]).resolve()
        target_path = Path(pair["target"]).resolve()

        if is_same_file(changed_path, source_path) or is_same_file(changed_path, target_path):
            return pair

    return None

def synchronize_files(pair, changed_file):
    """Synchronize a pair of files"""
    source_path = Path(pair["source"])
    target_path = Path(pair["target"])
    changed_path = Path(changed_file)

    log_message(f"Processing synchronization for {pair['name']} files")

    def is_same_file(a: Path, b: Path) -> bool:
        try:
            if a.exists() and b.exists():
                return a.resolve().samefile(b.resolve())
        except Exception:
            pass
        return a.resolve() == b.resolve()

    # Determine which file was changed and which needs to be updated
    if is_same_file(changed_path, source_path):
        source = source_path
        target = target_path
        direction = "CLAUDE.md → AGENTS.md"
    else:
        source = target_path
        target = source_path
        direction = "AGENTS.md → CLAUDE.md"

    # Verify source file exists
    if not source.exists():
        log_message(f"Source file {source} does not exist!", "ERROR")
        return False

    # Read source content
    try:
        with open(source, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        log_message(f"Error reading {source}: {e}", "ERROR")
        return False

    # Check if content is essentially the same (ignoring whitespace)
    def normalize_content(text):
        return '\n'.join(line.strip() for line in text.split('\n') if line.strip())

    # If target exists, check if it actually needs updating
    if target.exists():
        try:
            with open(target, 'r', encoding='utf-8') as f:
                target_content = f.read()

            if normalize_content(content) == normalize_content(target_content):
                log_message(f"Files are already in sync ({direction})")
                return True
        except Exception as e:
            log_message(f"Error reading {target}: {e}", "ERROR")

    # Update target file
    try:
        # Ensure target directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Write the synchronized content
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)

        log_message(f"Successfully synchronized {pair['name']} ({direction})")
        log_message(f"Updated: {target}")

        return True

    except Exception as e:
        log_message(f"Error updating {target}: {e}", "ERROR")
        return False

def main():
    """Main hook function — reads PostToolUse JSON from stdin."""
    try:
        # Read hook input from stdin (Claude Code hook protocol)
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        cwd = input_data.get("cwd", "")

        # Only process Write/Edit events
        if tool_name not in ("Write", "Edit"):
            sys.exit(0)

        # Extract file path from tool input
        changed_file = tool_input.get("file_path", "")
        if not changed_file:
            sys.exit(0)

        # Use cwd from hook input to resolve relative paths correctly
        project_dir = Path(cwd).resolve() if cwd else Path.cwd().resolve()

        # Convert to absolute path (anchor to project cwd, not process cwd)
        changed_path = Path(changed_file)
        if not changed_path.is_absolute():
            changed_file = (project_dir / changed_path).resolve()
        else:
            changed_file = changed_path.resolve()

        log_message(f"File change detected: {changed_file}")

        # Check if this file should trigger synchronization
        if not should_sync_file(changed_file):
            sys.exit(0)

        # Get all file pairs
        file_pairs = get_file_pairs(project_dir)

        # Find the pair that contains the changed file
        pair = find_pair_for_file(changed_file, file_pairs)

        if not pair:
            log_message("No matching file pair found")
            sys.exit(0)

        # Perform synchronization
        success = synchronize_files(pair, changed_file)

        if success:
            log_message("Synchronization completed successfully")
        else:
            log_message("Synchronization failed", "WARNING")

        # Always exit 0 — never block operations due to sync issues
        sys.exit(0)

    except json.JSONDecodeError:
        # Can't parse input — pass through
        sys.exit(0)
    except Exception as e:
        log_message(f"Unexpected error: {e}", "ERROR")
        # Never block operations due to hook errors
        sys.exit(0)


if __name__ == "__main__":
    main()