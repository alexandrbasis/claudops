---
name: update-setup
description: >-
  Pull upstream workflow changes from claudops into a local .claude/ folder.
  Uses a deterministic scan/report/apply engine, asks for approval before writes,
  and only touches upstream-tracked workflow files. Use when asked to update setup,
  pull workflow changes, sync claude config, update workflows, update skills,
  check for updates, or update-setup.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
  - Edit
  - AskUserQuestion
---

# Update Setup

> **Announcement**: "Checking for upstream workflow updates from **claudops**..."

Sync local `.claude/` workflow files with upstream claudops. The skill is
upstream-driven: local-only user files are ignored unless they are explicitly tracked in
the update manifest.

## Hard Rules

- Start with the deterministic script. Do not classify diffs manually.
- Ask for explicit approval before applying updates, refreshing disabled files, deleting
  removed upstream files, branch creation, commit, push, or PR creation.
- Never update `.claude/settings.json`, `.claude/settings.local.json`, `CLAUDE.md`,
  hook logs, `.gitkeep`, or local-only `*.local.*` files through this skill.
- Use LLM judgment only to explain conflicts and help the user choose a strategy after
  the script has produced exact statuses and diffs.

## Script

Use:

```bash
python3 .claude/skills/update-setup/scripts/update_setup.py --help
```

The script writes adoption state to:

```text
.claude/skills/update-setup/claudops-upstream.lock.json
```

Tracked scope:

- `.claude/**`

Skipped scope:

- `.claude/settings.json`
- `.claude/settings.local.json`
- `.claude/hooks/logs/**`
- `.gitkeep`
- `CLAUDE.md`
- local-only `*.local.*`

## Workflow

### 1. Scan

Create a deterministic report:

```bash
python3 .claude/skills/update-setup/scripts/update_setup.py scan \
  --output .claudops-update-report.json
```

For local testing against an existing upstream clone:

```bash
python3 .claude/skills/update-setup/scripts/update_setup.py scan \
  --upstream-root /tmp/claudops-upstream-sync \
  --commit "$(git -C /tmp/claudops-upstream-sync rev-parse HEAD)" \
  --output .claudops-update-report.json
```

### 2. Present Report

Render the report:

```bash
python3 .claude/skills/update-setup/scripts/update_setup.py report \
  --report .claudops-update-report.json
```

Explain statuses:

- `new`: upstream file is not present locally.
- `modified`: upstream differs from local and local has no tracked conflict.
- `conflicting`: local changed since the last tracked adoption.
- `disabled`: upstream file exists, but local has `<path>.disabled`.
- `removed`: file was tracked in the manifest but is gone upstream.
- `placeholder_only`: differences are filled `{{PLACEHOLDER}}` values.
- `unchanged`: local matches upstream or the tracked adoption hash.

If only `unchanged` and `placeholder_only` entries exist, report that the setup is up to
date and stop.

### 3. Ask for Approval

Ask which exact paths to update, refresh, or delete. Paths are relative to `.claude/`.
Convert approval into a selection JSON file:

```json
{
  "update": [
    "skills/example/SKILL.md"
  ],
  "refresh_disabled": [
    "skills/disabled/SKILL.md"
  ],
  "delete": [
    "skills/removed/SKILL.md"
  ]
}
```

Rules:

- `update` may include `new` and `modified` paths.
- `refresh_disabled` may include `disabled` paths and writes `<path>.disabled`.
- `delete` may include only `removed` paths.
- Do not apply `conflicting` paths until the user chooses a conflict strategy.

### 4. Apply

After approval:

```bash
python3 .claude/skills/update-setup/scripts/update_setup.py apply \
  --report .claudops-update-report.json \
  --selection /path/to/selection.json
```

The apply step updates selected files and refreshes the lock manifest.

### 5. Verify

Run:

```bash
python3 .claude/skills/update-setup/scripts/update_setup.py verify
```

When changing this skill itself, also run:

```bash
python3 .claude/skills/update-setup/tests/test_update_setup.py
```

## Conflict Handling

For `conflicting` files:

1. Show the file path and exact diff from `.claudops-update-report.json`.
2. Explain what upstream changed and what local changed.
3. Ask the user to choose one strategy:
   - replace local with upstream
   - keep local and mark skipped
   - manually merge, then update the manifest after verification

Do not silently merge conflicts.

## Post-Update Checks

After applying selected updates:

- Run `verify`.
- If new hook files were added, inspect `.claude/settings.json` and report unwired hooks
  as manual follow-up. Do not auto-edit settings.
- If updated files contain `{{PLACEHOLDER}}`, tell the user to run `/setup`.
- Summarize counts: updated, disabled refreshed, deleted, skipped, placeholders, and
  manual follow-ups.

## Edge Cases

- Clone failure: report the git error and stop.
- Missing `.claude/`: tell the user to clone the workflow repo first or run `/setup`.
- More than five `conflicting` files: warn this is a major update and suggest reviewing
  upstream commits before applying.
- Binary files: the script may copy them, but conflict explanation should avoid trying to
  summarize binary content.
