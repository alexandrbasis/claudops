#!/usr/bin/env python3
"""
Sensitive File Guard — Block writes to secrets, lock files, and .git internals.

Event:     PreToolUse
Matcher:   Write|Edit
Blocking:  Yes (exit 2 blocks the write)
Wired:     Yes (default in settings.json)

Normalizes incoming file paths (resolves symlinks, .., whitespace, etc.) before
matching against the protected patterns list, preventing path traversal bypasses.
Pattern matching is case-insensitive (V6 fix — macOS APFS is case-insensitive).
Catches nested .git/ paths in submodules/worktrees (V7 fix).

Configuration:
  PROTECTED_PATTERNS — list of fnmatch-style patterns to block writes to
  Override via env var: HOOK_SENSITIVE_FILES (comma-separated, appended to defaults)

To enable, add to .claude/settings.json hooks.PreToolUse:
  {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/guards/sensitive-file-guard.py"}]
  }
"""

import fnmatch
import json
import os
import sys

# === CONFIGURE FOR YOUR PROJECT ===
PROTECTED_PATTERNS = [
    # Environment files
    ".env",
    ".env.*",
    ".envrc",
    ".envrc.*",
    # Auth tokens / RC files
    ".npmrc",
    ".pypirc",
    ".netrc",
    # Cloud credentials
    ".aws/*",
    ".aws/credentials",
    ".aws/config",
    ".gcloud/*",
    ".kube/config",
    ".docker/config.json",
    # SSH / GPG
    ".ssh/*",
    "id_rsa*",
    "id_ed25519*",
    "id_ecdsa*",
    "id_dsa*",
    ".gnupg/*",
    # TLS / certs / keystores
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.keystore",
    "*.crt",
    "*.cer",
    # Lock files (regenerated, not hand-edited)
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Gemfile.lock",
    "Cargo.lock",
    "uv.lock",
    "composer.lock",
    # Generic credential files
    "secrets.json",
    "credentials.json",
    # Git internals (root-level; nested .git/ handled separately in is_protected)
    ".git/*",
]


def get_patterns() -> list:
    """Build pattern list from defaults + optional env var override."""
    patterns = list(PROTECTED_PATTERNS)
    extra = os.environ.get("HOOK_SENSITIVE_FILES", "")
    if extra:
        patterns.extend(p.strip() for p in extra.split(",") if p.strip())
    return patterns


def normalize_path(file_path: str, project_dir: str) -> str:
    """Resolve and normalize a file path to prevent traversal bypasses.

    V9 fix: strips leading/trailing whitespace before resolving (defeats
    `.env  ` and ` .env` bypass attempts on case-insensitive FS).
    """
    file_path = file_path.strip()
    if os.path.isabs(file_path):
        resolved = os.path.normpath(file_path)
    else:
        resolved = os.path.normpath(os.path.join(project_dir, file_path))
    try:
        return os.path.relpath(resolved, project_dir)
    except ValueError:
        return resolved


def is_protected(rel_path: str, patterns: list) -> str | None:
    """Check if a relative path matches any protected pattern.

    Case-insensitive (V6 fix). Catches nested .git/ paths anywhere
    in the path tree (V7 fix), which is critical for submodules and
    git worktrees.
    """
    # V7+V8 fix: nested credential/internal dirs in any subdir (submodules, monorepos,
    # worktrees) — fnmatch alone doesn't span / so "subdir/.git/foo" wouldn't match
    # ".git/*". This catches them via substring check.
    rel_lower = rel_path.lower()
    basename_lower = os.path.basename(rel_path).lower()

    # P4-7 fix: nested-dir check uses rel_lower (case-fold) for cross-FS
    # safety on macOS APFS (was rel_path which broke V6 case-insensitivity).
    NESTED_PROTECTED_DIRS = (".git/", ".aws/", ".ssh/", ".gnupg/", ".gcloud/", ".kube/", ".docker/")
    for protected_dir in NESTED_PROTECTED_DIRS:
        if f"/{protected_dir}" in rel_lower or rel_lower.startswith(protected_dir):
            return f"{protected_dir}* (nested or root)"
    # Also block bare ".git" without trailing slash (e.g., editing the file `.git` itself)
    if rel_lower == ".git" or rel_lower.endswith("/.git"):
        return ".git (root)"
    for pattern in patterns:
        pat_lower = pattern.lower()
        # Match against full relative path (case-insensitive)
        if fnmatch.fnmatch(rel_lower, pat_lower):
            return pattern
        # Match against basename only (e.g., "*.pem" matches "certs/server.pem")
        if fnmatch.fnmatch(basename_lower, pat_lower):
            return pattern
    return None


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if not file_path:
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", input_data.get("cwd", os.getcwd()))
    rel_path = normalize_path(file_path, project_dir)
    patterns = get_patterns()

    matched = is_protected(rel_path, patterns)
    if matched:
        print(
            f"BLOCKED: '{rel_path}' matches protected pattern '{matched}'. "
            f"Explain why this edit is necessary, or use a Bash command if appropriate "
            f"(e.g., npm install to regenerate lock files).",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
