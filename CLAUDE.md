# Project Rules

## Token Efficiency

- Be concise. Skip pleasantries. Lead with the answer.
- Don't restate the question. Don't summarize what you just did unless asked.
- If you can say it in one sentence, don't use three.

## Compact Output

- Use `--oneline`, `--short`, `--stat`, `--name-only` flags for git commands
- Pipe long output through `| tail -20` or `| head -30` — don't dump full logs
- Use `wc -l` to check size before reading large files
- For test output: use `--silent`, `--quiet`, or `--reporter=dot` when available
- For search: use `--files-with-matches` / `-l` before `--count` before full content

## Workflow

- Run `/setup` after cloning this `.claude/` folder into a new codebase
- Convention skills (`coding-conventions`, `review-conventions`) are preloaded into agents via `skills:` frontmatter — edit them to fine-tune project knowledge
- Product docs live in `product-docs/` — PRDs and JTBDs are source of truth, tasks reference them
