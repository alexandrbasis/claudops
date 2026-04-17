---
name: fci
description: >-
  Fix CI pipeline failures blocking PR merge. Use when CI checks fail,
  'pipeline broken', 'build failing', 'fix CI', or 'checks not passing'.
  NOT for debugging runtime bugs (use /dbg), NOT for code review (use /sr).
argument-hint: [workflow-name or run-id]
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
disable-model-invocation: true
---

# Fix CI Issues Command

Briefly tell the user you are using the fci skill before starting work,
so they know which workflow is running.

## PRIMARY OBJECTIVE
Fix all CI pipeline failures blocking the PR merge while maintaining code quality and test integrity.

## SCOPE
- Supports the project CI pipeline as configured in the repository
- If `$ARGUMENTS` specifies a workflow outside the project scope, inform the user and suggest manual investigation

## CONTEXT & CONSTRAINTS
- CI pipeline failed during merge attempt to main branch
- Must resolve all failures without compromising code quality
- Preserve existing test coverage and validation logic
- CI includes: {{LINT_CMD}}, {{TEST_CMD}}, {{BUILD_CMD}}, and any project-specific checks
- Do not silence CI with `any`, `@ts-ignore`, `// eslint-disable`, or
  architectural shortcuts — the goal is a real fix, not a green checkmark.
  If a suppression is genuinely correct (e.g. a `.d.ts` shim), flag it
  explicitly so the reviewer can confirm.
- Follow project architecture rules (see coding-conventions skill)

## RELATED SKILLS
- `/dbg` - Runtime bugs requiring instrumentation and evidence gathering
- `/sr` - Post-fix code review before re-attempting merge
- `/prc` - Addressing reviewer comments on the PR

## ANALYSIS REQUIREMENTS
1. **Identify CI Failures:**
   - Run `gh workflow list` if you are unsure of the workflow name.
   - Run `gh run list --limit=3` to check recent CI status.
   - Pick the most recent failing run and review its logs with
     `gh run view <run-id> --log`. Don't fetch logs for older runs unless
     the recent-run failures are ambiguous.
   - Categorize failures by type (linting, tests, types, build, other).

2. **Execute Diagnostic Checks (run in parallel):**
   - These commands are independent — batch them in one turn as parallel
     Bash tool calls, do not chain sequentially.
   - Ensure dependencies are installed first (sequential prerequisite).
   - Then in parallel: `{{LINT_CMD}}`, `{{TYPECHECK_CMD}}`, `{{TEST_CMD}}`,
     `{{BUILD_CMD}}`.
   - Collect all failure logs before choosing where to start fixing —
     don't stop at the first red check.

## RESOLUTION PROCESS

Scope discipline: fix only what the failing CI checks require. Do not
refactor nearby code, rename symbols for consistency, tighten unrelated
types, or add defensive error handling that wasn't failing. If you spot
adjacent problems, note them in the handoff summary — don't fix them in
this PR.

1. **Formatting (only if lint reported style violations):**
   - Skip this step entirely if formatting is clean.
   - Otherwise run `{{FORMAT_CMD}}`, then re-run lint to confirm the
     formatter didn't introduce new issues.

2. **Address Type Errors:**
   - Resolve typing errors surfaced by lint/test/typecheck output
   - Add precise typings rather than suppressing warnings

3. **Resolve Test Failures:**
   - Fix failing tests by correcting the implementation bug the test is
     catching — the test is a spec, so weakening assertions to turn the
     check green hides the real defect.
   - Maintain or improve test coverage (>=80% target). If a test is
     genuinely wrong (e.g. asserts outdated behavior), update it and
     explicitly flag the change in the handoff summary.

4. **Fix Linting Issues:**
   - Address linter violations
   - Update tests/fixtures when necessary rather than suppressing rules

5. **Security Issues:**
   - Address any dependency vulnerability findings that surface during investigation

6. **Build Issues:**
   - Ensure build succeeds
   - Fix any import or runtime errors

## VERIFICATION REQUIREMENTS
Before completion, run the full CI validation suite locally and confirm
every command exits zero:
```bash
# Run full CI validation suite
{{LINT_CMD}} && \
{{TYPECHECK_CMD}} && \
{{TEST_CMD}} && \
{{BUILD_CMD}}
```

Optional additional checks (if relevant jobs are failing):
```bash
# Coverage check
{{COVERAGE_CMD}}
```

## TROUBLESHOOTING
- `gh` auth failure: Run `gh auth status`; prompt user to run `gh auth login` if needed
- Docker not running: Run `docker info`; inform user to start Docker Desktop
- DB connection refused: Verify test database is running; check port conflicts
- Language version mismatch: Check version files (`.nvmrc`, `.tool-versions`, etc.) and use appropriate version manager

## DEFINITION OF DONE
- [ ] All CI checks pass (lint, typing, format, tests, build)
- [ ] Test coverage did not drop below the pre-fix baseline (>=80% floor).
- [ ] No test logic simplified or removed
- [ ] Security vulnerabilities resolved (if applicable)
- [ ] Build succeeds
- [ ] GitHub CI status shows green checkmark
- [ ] Ready for clean merge to main branch
