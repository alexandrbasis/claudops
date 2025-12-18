#!/usr/bin/env python3
"""
Claude/Agents Files Synchronization Hook

This hook ensures that claude.md and agents.md files stay synchronized across the entire project.
When changes are detected in either file, the corresponding counterpart is updated automatically.

File pairs to synchronize:
1. Root: claude.md ↔ agents.md
2. Backend: backend/claude.md ↔ backend/AGENTS.md
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")
    sys.stdout.flush()

def calculate_file_hash(file_path):
    """Calculate MD5 hash of file content"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None

def get_file_pairs(base_path):
    """Define the file pairs that should be synchronized"""
    project_root = Path(base_path).parent

    return [
        {
            "source": project_root / "CLAUDE.md",
            "target": project_root / "AGENTS.md",
            "name": "Root"
        },
        {
            "source": project_root / "backend" / "CLAUDE.md",
            "target": project_root / "backend" / "AGENTS.md",
            "name": "Backend"
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

    for pair in file_pairs:
        source_path = Path(pair["source"]).resolve()
        target_path = Path(pair["target"]).resolve()

        if changed_path == source_path or changed_path == target_path:
            return pair

    return None

def synchronize_files(pair, changed_file):
    """Synchronize a pair of files"""
    source_path = Path(pair["source"])
    target_path = Path(pair["target"])
    changed_path = Path(changed_file)

    log_message(f"Processing synchronization for {pair['name']} files")

    # Determine which file was changed and which needs to be updated
    if changed_path == source_path:
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
    """Main hook function"""
    # Get the repository root directory
    repo_root = Path(__file__).parent.parent

    # Get the changed file from environment variable or command line argument
    changed_file = os.environ.get('FILE_PATH', '')
    if len(sys.argv) > 1:
        changed_file = sys.argv[1]

    if not changed_file:
        log_message("No file path provided", "ERROR")
        sys.exit(1)

    # Convert to absolute path
    changed_file = Path(changed_file).resolve()

    log_message(f"File change detected: {changed_file}")

    # Check if this file should trigger synchronization
    if not should_sync_file(changed_file):
        log_message("File does not require synchronization")
        sys.exit(0)

    # Get all file pairs
    file_pairs = get_file_pairs(repo_root)

    # Find the pair that contains the changed file
    pair = find_pair_for_file(changed_file, file_pairs)

    if not pair:
        log_message("No matching file pair found", "ERROR")
        sys.exit(1)

    # Perform synchronization
    success = synchronize_files(pair, changed_file)

    if success:
        log_message("Synchronization completed successfully")
        sys.exit(0)
    else:
        log_message("Synchronization failed", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()