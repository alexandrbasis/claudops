# Setup Guide: Wythm Claude Code Workflows

This guide will help you set up and use the Claude Code workflows from this repository in your own projects.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Full Installation](#full-installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Claude Code** - [Installation Guide](https://docs.anthropic.com/en/docs/claude-code/setup)
- **Python 3.11+** - Required for hooks
- **Node.js 18+** - Required for project-specific tools
- **Git** - Version control
- **GitHub CLI (`gh`)** - For PR automation: `brew install gh` (macOS)
- **rsync** - For file syncing (usually pre-installed on macOS/Linux)

### Optional Dependencies

- **Gemini CLI** - For cross-AI plan review: `npm i -g @google/gemini-cli`
- **Linear Account** - For Linear integration features

## Quick Start

### Option 1: Copy Individual Components

Pick specific agents, skills, or hooks that interest you:

```bash
# Clone this repository
git clone https://github.com/alexandrbasis/wythm-claude-workflows.git

# Copy specific components to your project
cp wythm-claude-workflows/.claude/agents/code-review-agents/security-code-reviewer.md \
   your-project/.claude/agents/

cp -r wythm-claude-workflows/.claude/skills/si \
   your-project/.claude/skills/
```

### Option 2: Copy Entire Configuration

For a complete setup:

```bash
# Clone this repository
git clone https://github.com/alexandrbasis/wythm-claude-workflows.git

# Copy entire .claude directory
cp -r wythm-claude-workflows/.claude your-project/

# Important: Remove or customize hooks to avoid conflicts
rm -rf your-project/.claude/hooks/*
```

## Full Installation

### Step 1: Clone Repository

```bash
cd ~/projects
git clone https://github.com/alexandrbasis/wythm-claude-workflows.git
cd wythm-claude-workflows
```

### Step 2: Review Components

Explore what's available:

```bash
# List all agents
ls -la .claude/agents/

# List all skills
ls -la .claude/skills/

# List all hooks
ls -la .claude/hooks/

# List all rules
ls -la .claude/rules/
```

### Step 3: Copy to Your Project

```bash
# Navigate to your project
cd /path/to/your/project

# Create .claude directory if it doesn't exist
mkdir -p .claude/{agents,hooks,skills,rules,scripts}

# Copy components you want to use
cp ~/projects/wythm-claude-workflows/.claude/agents/code-review-agents/*.md .claude/agents/
cp -r ~/projects/wythm-claude-workflows/.claude/skills/si .claude/skills/
```

### Step 4: Configure Settings

Create `.claude/settings.local.json` in your project:

```json
{
  "env": {
    "PUBLIC_REPO_PATH": "/path/to/your/public/repo"
  },
  "permissions": {
    "allow": [
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)"
    ]
  }
}
```

**Important**: Add `.claude/settings.local.json` to your `.gitignore`:

```bash
echo ".claude/settings.local.json" >> .gitignore
```

### Step 5: Make Hooks Executable

```bash
chmod +x .claude/hooks/**/*.py
chmod +x .claude/scripts/*.sh
```

## Configuration

### Hook Configuration

#### Enable Hookify Rules Engine

The hookify system provides declarative behavior rules. Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hookify/hooks/pretooluse.py\"",
            "timeout": 30
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash|Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hookify/hooks/posttooluse.py\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

#### Enable Cross-AI Plan Review (Gemini)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/scripts/review-plan-gemini.sh",
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

#### Enable Auto-Lint on Write

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/lint/lint-on-write.py\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### MCP Server Configuration

For Linear integration, configure MCP in Claude Code's global settings:

```bash
# Edit global MCP config
code ~/.claude/mcp/linear.json
```

Add Linear API key:

```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "@linear/mcp-server"],
      "env": {
        "LINEAR_API_KEY": "your-linear-api-key"
      }
    }
  }
}
```

## Usage

### Using Agents

Agents are automatically available once placed in `.claude/agents/`. Claude uses them when spawning subagents for specific tasks:

```
# Code review with security focus
"Please review this code for security issues"
→ Claude will use the security-code-reviewer agent

# Architecture review
"Review this feature's architecture"
→ Claude will use the senior-architecture-reviewer agent
```

### Using Skills

Skills in `.claude/skills/` are invoked via slash commands or triggered automatically:

```bash
# Create a task
/ct

# Start TDD implementation
/si

# Code review
/sr

# Brainstorm ideas
/brainstorm

# Debug an issue
/dbg

# Sync to public repo
/sync-public
```

See [.claude/skills/README.md](../.claude/skills/README.md) for the full skill catalog.

### Using Hooks

Hooks run automatically when configured. View hook execution logs:

```bash
tail -f .claude/hooks/logs/hook-debug.log
```

### Using Rules

Rules in `.claude/rules/` are automatically loaded based on file globs and provide context-specific guidelines (backend architecture, testing patterns, git conventions, etc.).

## Customization

### Creating Custom Agents

Create a new file in `.claude/agents/your-category/`:

```markdown
# Your Agent Name

You are a specialized agent for [specific task].

## Capabilities
- Capability 1
- Capability 2

## Process
1. Step 1
2. Step 2

## Output Format
Provide results in the following format:
...
```

### Creating Custom Skills

Use the `/skill-creator` skill or create manually:

1. Create a directory in `.claude/skills/your-skill/`
2. Add a `SKILL.md` file with the skill definition
3. Optionally add reference files for additional context

```markdown
# Your Skill Name

Description of when and how to use this skill.

## Trigger
When the user asks to [do something specific].

## Process
1. Step 1
2. Step 2

## Output
Expected output format.
```

### Creating Custom Hookify Rules

Create a `.local.md` file in `.claude/hooks/hookify/rules/`:

```markdown
# Rule Name

## Trigger
- event: PreToolUse
- tool: Bash

## Condition
command contains "rm -rf"

## Action
BLOCK with message: "Dangerous rm command blocked. Please be more specific."
```

## Troubleshooting

### Hooks Not Running

1. Check hook is executable:
   ```bash
   ls -la .claude/hooks/
   ```

2. Check settings.json syntax:
   ```bash
   python3 -m json.tool .claude/settings.json
   ```

3. Check hook logs:
   ```bash
   tail -f .claude/hooks/logs/hook-debug.log
   ```

### Permission Errors

Add tool permissions in `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(your-command:*)"
    ]
  }
}
```

### MCP Servers Not Working

1. Verify MCP server installation:
   ```bash
   npx -y @linear/mcp-server --version
   ```

2. Check MCP logs:
   ```bash
   tail -f ~/.claude/logs/mcp-*.log
   ```

### Sync Script Failing

1. Check rsync is installed:
   ```bash
   which rsync
   ```

2. Verify public repo path:
   ```bash
   echo $PUBLIC_REPO_PATH
   ls -la "$PUBLIC_REPO_PATH"
   ```

3. Check sync logs:
   ```bash
   tail -f .claude/sync-public.log
   ```

## Best Practices

1. **Start Small** - Copy individual components first, then expand
2. **Test Hooks** - Test hooks manually before enabling automation
3. **Backup Settings** - Keep a backup of your `.claude/settings.local.json`
4. **Review Logs** - Regularly check hook logs for issues
5. **Customize Paths** - Update all absolute paths to match your system
6. **Secure Secrets** - Never commit `.claude/settings.local.json`

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/alexandrbasis/wythm-claude-workflows/issues)
- **Claude Code Docs**: [Official Documentation](https://docs.anthropic.com/en/docs/claude-code)
- **Main Project**: [Wythm Repository](https://github.com/alexandrbasis/wythm)

---

**Need more help?** Open an issue on GitHub or check the [main project documentation](https://github.com/alexandrbasis/wythm).
