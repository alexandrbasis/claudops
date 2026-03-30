#!/bin/bash
# Guard: file content safety checks
# Spawns only when "if" matches: .ts or schema.prisma files
# Replaces hookify rules: schema-change, arch-violation, interface-naming, no-console
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.new_string // .tool_input.content // ""')

# Rule: schema-change — any edit to schema.prisma requires migration workflow
if echo "$FILE_PATH" | grep -q 'schema\.prisma$'; then
  echo "BLOCKED: Schema change requires migration workflow. Run: cd backend && npm run prisma:migrate:dev -- --name <change> --create-only" >&2
  exit 2
fi

# Rules below apply only to .ts files
echo "$FILE_PATH" | grep -q '\.ts$' || exit 0

# Rule: arch-violation — no infrastructure imports in core layer
if echo "$FILE_PATH" | grep -q '/src/core/'; then
  if echo "$CONTENT" | grep -qE "from[[:space:]]+['\"]@?infrastructure|from[[:space:]]+['\"].*prisma|import.*PrismaService|import.*Controller"; then
    echo "BLOCKED: Infrastructure import in Core layer. Use port interface instead." >&2
    exit 2
  fi
fi

# Rules below apply only to backend .ts files
echo "$FILE_PATH" | grep -q '/backend/src/' || exit 0

# Rule: interface-naming — interfaces must start with I prefix
# Uses perl for negative lookahead (not available in BSD grep)
if echo "$CONTENT" | perl -ne 'exit 1 if /export\s+interface\s+(?!I[A-Z])[A-Z]\w+/' 2>/dev/null; [ $? -eq 1 ]; then
  echo "BLOCKED: Interface must start with 'I' prefix (e.g. IUserRepository)." >&2
  exit 2
fi

# Rule: no-console — use NestJS Logger instead
# Filter out commented lines, then check for console usage
if echo "$CONTENT" | grep -vE '^\s*//' | grep -qE 'console\.(log|warn|error|info|debug)\('; then
  echo "BLOCKED: Use NestJS Logger instead of console.log. Example: private readonly logger = new Logger(MyService.name);" >&2
  exit 2
fi

exit 0
