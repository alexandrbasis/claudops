# Codex CLI Prompt Templates

Reusable prompt templates for common Codex operations.

## Approach Validation

### General Approach Review
```bash
codex exec "Review this implementation approach:

## Goal
[What you're trying to achieve]

## Proposed Approach
[Your planned implementation]

## Key Decisions
- [Decision 1]
- [Decision 2]

Questions:
1. Is this approach sound?
2. What are the potential issues?
3. What alternatives should I consider?" -m gpt-5.2-codex --full-auto
```

### Architecture Decision
```bash
codex exec "I need to decide between these approaches for [feature]:

Option A: [Description]
- Pros: [...]
- Cons: [...]

Option B: [Description]
- Pros: [...]
- Cons: [...]

Context: [Project context]
Requirements: [Key requirements]

Which approach would you recommend and why?" -m gpt-5.2-codex --full-auto
```

## Code Review

### Uncommitted Changes Review
```bash
codex exec review --uncommitted -m gpt-5.2-codex --full-auto
```

### Review Against Branch
```bash
codex exec review --base main -m gpt-5.2-codex --full-auto
```

### Review Specific Commit
```bash
codex exec review --commit [SHA] -m gpt-5.2-codex --full-auto
```

### Custom Review Focus
```bash
codex exec "Review the uncommitted changes focusing on:
1. [Focus area 1]
2. [Focus area 2]
3. [Focus area 3]

Provide specific feedback for each area." -m gpt-5.2-codex --full-auto
```

## Security Review

### General Security Audit
```bash
codex exec "Perform a security review of the uncommitted changes. Check for:
- SQL/NoSQL injection
- XSS vulnerabilities
- Command injection
- Authentication/authorization issues
- Sensitive data exposure
- Input validation gaps

Report findings with severity levels (Critical/High/Medium/Low)." -m gpt-5.2-codex --full-auto
```

### API Security Review
```bash
codex exec "Review [file/endpoint] for API security:
- Rate limiting
- Input validation
- Authentication checks
- Authorization (access control)
- Error handling (info leakage)
- CORS configuration" -m gpt-5.2-codex --full-auto
```

## Implementation Verification

### Feature Completion Check
```bash
codex exec "Verify implementation of [feature] is complete.

Requirements:
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

Key files:
- [file1]
- [file2]

Check:
- All requirements implemented?
- Edge cases handled?
- Error handling adequate?
- Tests cover key paths?" -m gpt-5.2-codex --full-auto
```

### Refactoring Verification
```bash
codex exec "Verify this refactoring preserves behavior:

Original behavior: [description]
Changed files: [files]

Check that:
1. All existing functionality preserved
2. No subtle behavior changes
3. No new edge case bugs introduced" -m gpt-5.2-codex --full-auto
```

## Test Assessment

### Test Coverage Review
```bash
codex exec "Review test coverage for [file/module].

Key functionality:
- [Function 1]
- [Function 2]

Check:
- Are all public functions tested?
- Are edge cases covered?
- Are error paths tested?
- What's missing?" -m gpt-5.2-codex --full-auto
```

### Test Quality Review
```bash
codex exec "Review the quality of tests in [test file]:
- Are tests meaningful or just checking syntax?
- Are assertions comprehensive?
- Are tests isolated (no shared state)?
- Are tests readable/maintainable?" -m gpt-5.2-codex --full-auto
```

## Performance Review

### Performance Analysis
```bash
codex exec "Analyze [file/function] for performance issues:
- Inefficient algorithms (O(n^2) etc.)
- Memory leaks or excessive allocation
- Blocking operations
- Missing caching opportunities
- N+1 query patterns" -m gpt-5.2-codex --full-auto
```

## Bug Investigation

### Bug Root Cause Analysis
```bash
codex exec "Help investigate this bug:

Symptom: [What's happening]
Expected: [What should happen]
Context: [Relevant context]
Suspected files: [files]

Find the root cause and suggest a fix." -m gpt-5.2-codex --full-auto
```

## Template Variables

Use these placeholders:
- `[feature]` - Feature name/description
- `[file]` - File path
- `[SHA]` - Git commit hash
- `[description]` - Brief description
- `[requirements]` - List of requirements
