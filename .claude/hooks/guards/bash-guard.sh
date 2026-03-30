#!/bin/bash
# Guard: bash command safety checks
# Spawns only when "if" matches: rm, prisma, or npm run test commands
# Replaces hookify rules: dangerous-rm, db-danger, test-silent
COMMAND=$(jq -r '.tool_input.command')

# Rule: dangerous-rm — block rm -rf on critical directories
if echo "$COMMAND" | grep -qE 'rm[[:space:]]+(-rf|-fr)[[:space:]]' && echo "$COMMAND" | grep -qE '(node_modules|src|backend|prisma)'; then
  echo "BLOCKED: rm -rf targets critical directory. Use 'mv <path> ~/.Trash/' instead." >&2
  exit 2
fi
if echo "$COMMAND" | grep -qE 'rm[[:space:]]+(-rf|-fr)[[:space:]]+(\/|~)$'; then
  echo "BLOCKED: rm -rf targets root or home directory." >&2
  exit 2
fi

# Rule: db-danger — block destructive Prisma commands
if echo "$COMMAND" | grep -qE 'prisma[[:space:]]+(migrate[[:space:]]+reset|db[[:space:]]+push)'; then
  echo "BLOCKED: Destructive Prisma command. Use: npm run prisma:migrate:dev -- --name <change> --create-only" >&2
  exit 2
fi
if echo "$COMMAND" | grep -qE 'prisma[[:space:]]+migrate[[:space:]]+dev' && ! echo "$COMMAND" | grep -q '\-\-create-only'; then
  echo "BLOCKED: prisma migrate dev without --create-only. Use: npm run prisma:migrate:dev -- --name <change> --create-only" >&2
  exit 2
fi

# Rule: test-silent — enforce :silent test variants
if echo "$COMMAND" | grep -qE 'npm[[:space:]]+run[[:space:]]+test' && ! echo "$COMMAND" | grep -q ':silent'; then
  echo "BLOCKED: Use silent test variant. Replace: npm run test → npm run test:silent" >&2
  exit 2
fi

exit 0
