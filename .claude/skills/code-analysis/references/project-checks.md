# Project-Specific Analysis Checks

Detailed commands for project-specific code analysis. Read this when analyzing the project codebase.

## Generic Codebase Metrics

These checks work for any project.

```bash
# Total source file count
find {{SRC_DIR}} -type f -name "*.{{LANGUAGE}}" 2>/dev/null | wc -l

# Test file count
find {{TEST_DIR}} -type f -name "*.test.*" -o -name "*.spec.*" 2>/dev/null | wc -l

# Lines of code (source, excluding tests)
find {{SRC_DIR}} -type f -name "*.{{LANGUAGE}}" | xargs wc -l 2>/dev/null | tail -1

# Dependency count
cat package.json 2>/dev/null | jq '.dependencies | length' || \
cat requirements.txt 2>/dev/null | wc -l || \
cat go.mod 2>/dev/null | grep -c "require" || \
echo "Unknown package manager"
```

## Error Handling Patterns

```bash
# Raw Error throws (should use domain exceptions instead)
grep -rn "throw new Error(" {{SRC_DIR}} --include="*.ts" --include="*.js" \
  | grep -v "node_modules\|spec\|test"

# Empty catch blocks (swallowed errors)
grep -rn "catch.*{" {{SRC_DIR}} --include="*.ts" --include="*.js" \
  | grep -v "node_modules\|spec\|test"

# TODO/FIXME/HACK markers
grep -rn "TODO\|FIXME\|HACK\|XXX" {{SRC_DIR}} --include="*.ts" --include="*.js" --include="*.py" \
  | grep -v "node_modules\|__pycache__"
```

## Configuration & Security

```bash
# Hardcoded secrets (potential)
grep -rn "password\|secret\|api_key\|apikey\|token" {{SRC_DIR}} --include="*.ts" --include="*.js" --include="*.py" \
  | grep -v "node_modules\|test\|spec\|\.env\.example\|__pycache__"

# Environment variable usage
grep -rn "process\.env\|os\.environ\|env\.get" {{SRC_DIR}} --include="*.ts" --include="*.js" --include="*.py" \
  | grep -v "node_modules\|__pycache__"

# Config files present
ls {{CONFIG_FILES}} 2>/dev/null
```

## Architecture Layer Checks

```bash
# File distribution across top-level directories
for dir in {{SRC_DIR}}/*/; do
  echo "$(basename "$dir"): $(find "$dir" -type f | wc -l) files"
done

# Circular dependency risk: files importing from parent directories
grep -rn "from '\.\.\/" {{SRC_DIR}} --include="*.ts" --include="*.js" 2>/dev/null | head -20
```

## Schema / Data Model Health

```bash
# Schema file stats (if schema path configured)
wc -l {{SCHEMA_PATH}} 2>/dev/null || echo "No schema file configured"

# Migration count (if migrations directory exists)
find . -path "*/migrations/*" -type f 2>/dev/null | wc -l
```

## Project-Specific Checks

{{PROJECT_SPECIFIC_CHECKS}}
