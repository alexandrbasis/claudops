# Gemini CLI Tools

This file summarizes the key built-in tools you can rely on when using Gemini CLI.

In most cases you **do not call tools directly**. You describe the task, and Gemini selects tools. You can still nudge tool usage (“use Google Search”, “fetch this URL”, etc.).

## Web search tool (`google_web_search`)

Use when you need **current** information from the web (latest versions, docs changes, benchmarks).

Example prompt:

```bash
gemini --model gemini-3-pro-preview "What's new in TypeScript? Use Google Search and cite sources." --output-format text
```

## Web fetch tool (`web_fetch`)

Use when you want Gemini to **summarize / compare / extract** info from specific URLs.

Example prompt:

```bash
gemini --model gemini-3-pro-preview "Summarize the main points of https://example.com/docs" --output-format text
```

## Shell tool (`run_shell_command`)

Use when the task requires executing local commands (build, tests, git, etc.). Treat it as powerful and potentially dangerous; prefer narrower instructions.

Example prompt:

```bash
gemini --model gemini-3-pro-preview "Run tests, then summarize failures. Use shell commands as needed." --output-format text
```

## File system tools

Gemini CLI includes a suite of file-system tools (read/write/search/etc.) for working with your local workspace.

When you want Gemini to understand code, you’ll usually get the best results by injecting files via `@path`:

```bash
gemini --model gemini-3-pro-preview "@src/ Summarize the architecture and main flows." --output-format text
```

## Tool stats in JSON output

If you run with `--output-format json`, tool usage appears under `.stats.tools`.

```bash
gemini --model gemini-3-pro-preview "Search the web for the latest Node LTS and summarize." --output-format json > /tmp/gemini.json
jq '.stats.tools' /tmp/gemini.json
```

## Restricting risky shell usage (settings)

The docs describe restricting shell commands via settings (e.g. allowing only certain commands or excluding `rm`, `git push`, etc.). If you need tighter safety, configure `run_shell_command` restrictions in `~/.gemini/settings.json` or `.gemini/settings.json`.

## Image generation (nanobanana extension)

This workspace has the `nanobanana` extension installed (see `image-generation.md`).

Quick start (interactive):

```bash
gemini --model gemini-3-pro-preview
```

Then run:
- `/generate "..."` to generate images
- `/edit <file> "..."` to edit
- `/restore <file> "..."` to restore

Note: to switch the underlying **image model** to “Pro”, set:
- `NANOBANANA_MODEL=gemini-3-pro-image-preview` (this workspace’s default)
