---
description: Create hooks to prevent unwanted behaviors from conversation analysis or explicit instructions
argument-hint: Optional specific behavior to address
allowed-tools: ["Read", "Write", "AskUserQuestion", "Task", "Grep", "TodoWrite", "Skill"]
---

# Hookify - Create Hooks from Unwanted Behaviors

**FIRST: Load the hookify:writing-rules skill** using the Skill tool to understand rule file format and syntax.

Create hook rules to prevent problematic behaviors by analyzing the conversation or from explicit user instructions.

## Your Task

You will help the user create hookify rules to prevent unwanted behaviors. Follow these steps:

### Step 1: Gather Behavior Information

**If $ARGUMENTS is provided:**
- User has given specific instructions: `$ARGUMENTS`
- Still analyze recent conversation (last 10-15 user messages) for additional context
- Look for examples of the behavior happening

**If $ARGUMENTS is empty:**
- Launch the conversation-analyzer agent to find problematic behaviors
- Agent will scan user prompts for frustration signals
- Agent will return structured findings

**To analyze conversation:**
Use the Task tool to launch conversation-analyzer agent:
```
{
  "subagent_type": "hookify:conversation-analyzer",
  "description": "Analyze conversation for unwanted behaviors",
  "prompt": "Analyze the current conversation to find behaviors to prevent."
}
```

### Step 2: Present Findings to User

After gathering behaviors (from arguments or agent), present to user using AskUserQuestion:

**Question 1: Which behaviors to hookify?**
- Header: "Create Rules"
- multiSelect: true
- Options: List each detected behavior (max 4)
  - Label: Short description (e.g., "Block rm -rf")
  - Description: Why it's problematic

**Question 2: For each selected behavior, ask about action:**
- "Should this block the operation or just warn?"
- Options:
  - "Just warn" (action: warn - shows message but allows)
  - "Block operation" (action: block - prevents execution)

### Step 3: Generate Rule Files

**IMPORTANT**: Rules go in `.claude/hookify/rules/` directory (project-local hookify).

For each confirmed behavior, create a `.claude/hookify/rules/{rule-name}.local.md` file:

**Rule naming convention:**
- Use kebab-case
- Be descriptive: `block-dangerous-rm`, `warn-console-log`, `require-tests-before-stop`
- Start with action verb: block, warn, prevent, require

**File format:**
```markdown
---
name: {rule-name}
enabled: true
event: {bash|file|stop|prompt|all}
pattern: {regex pattern}
action: {warn|block}
---

{Message to show Claude when rule triggers}
```

**Action values:**
- `warn`: Show message but allow operation (default)
- `block`: Prevent operation or stop session

**For more complex rules (multiple conditions):**
```markdown
---
name: {rule-name}
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$
  - field: new_text
    operator: contains
    pattern: API_KEY
---

{Warning message}
```

### Step 4: Create Files and Confirm

1. Check if `.claude/hookify/rules/` directory exists
   - If not, create it first with: `mkdir -p .claude/hookify/rules`

2. Use Write tool to create each `.claude/hookify/rules/{name}.local.md` file

3. Show user what was created:
   ```
   Created 3 hookify rules:
   - .claude/hookify/rules/dangerous-rm.local.md
   - .claude/hookify/rules/console-log.local.md
   - .claude/hookify/rules/sensitive-files.local.md

   These rules will trigger on:
   - dangerous-rm: Bash commands matching "rm -rf"
   - console-log: Edits adding console.log statements
   - sensitive-files: Edits to .env or credentials files
   ```

4. Inform user: **"Rules are active immediately - no restart needed!"**

## Event Types Reference

- **bash**: Matches Bash tool commands
- **file**: Matches Edit, Write, MultiEdit tools
- **stop**: Matches when agent wants to stop (use for completion checks)
- **prompt**: Matches when user submits prompts
- **all**: Matches all events

## Pattern Writing Tips

**Bash patterns:**
- Match dangerous commands: `rm\s+-rf|chmod\s+777|dd\s+if=`
- Match specific tools: `npm\s+install\s+|pip\s+install`

**File patterns:**
- Match code patterns: `console\.log\(|eval\(|innerHTML\s*=`
- Match file paths: `\.env$|\.git/|node_modules/`

## Important Notes

- **No restart needed**: Rules take effect immediately on the next tool use
- **File location**: Create files in `.claude/hookify/rules/` directory
- **Regex syntax**: Use Python regex syntax
- **Action types**: Rules can `warn` (default) or `block` operations

Use TodoWrite to track your progress through the steps.
