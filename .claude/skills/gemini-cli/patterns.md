# Gemini CLI Integration Patterns

Advanced patterns for orchestrating Gemini CLI effectively from Claude Code.

## Pattern 1: Generate-Review-Fix Cycle

The most reliable pattern for quality code generation.

```bash
# Step 1: Generate code
gemini --model gemini-3-pro-preview "Create [code description]" --yolo --output-format text

# Step 2: Have Gemini review its own work
gemini --model gemini-3-pro-preview "Review @path/to/generated/file for bugs and security issues" --output-format text

# Step 3: Fix identified issues
gemini --model gemini-3-pro-preview "Fix these issues in @path/to/file: [list from review]. Apply now." --yolo --output-format text
```

### Why It Works
- Different "mindset" for generation vs review
- Self-correction catches common mistakes
- Security vulnerabilities often caught in review phase

### Example
```bash
# Generate
gemini --model gemini-3-pro-preview "Create a user authentication module with bcrypt and JWT" --yolo --output-format text

# Review
gemini --model gemini-3-pro-preview "Review @auth.js for security vulnerabilities" --output-format text
# Output: "Found XSS risk, missing input validation, weak JWT secret"

# Fix
gemini --model gemini-3-pro-preview "Fix in @auth.js: XSS risk, add input validation, use env var for JWT secret. Apply now." --yolo --output-format text
```

## Pattern 2: JSON Output for Programmatic Processing

Use JSON output when you need to process results programmatically.

```bash
gemini --model gemini-3-pro-preview "[prompt]" --output-format json > /tmp/gemini.json 2> /tmp/gemini.err
```

### Final-output-only extraction

If you want just the final answer (and minimal noise), extract `.response` into a separate file:

```bash
gemini --model gemini-3-pro-preview "Output ONLY the final answer. No reasoning. Task: [prompt]" \
  --output-format json \
  > /tmp/gemini.json 2> /tmp/gemini.err \
  && jq -r '.response' /tmp/gemini.json > /tmp/gemini.out \
  && echo "Gemini completed"
```

### Parsing the Response

```javascript
// In Node.js or with jq
const result = JSON.parse(output);
const content = result.response;
const [modelName] = Object.keys(result.stats.models ?? {});
const tokenUsage = modelName ? result.stats.models[modelName]?.tokens?.total : undefined;
const toolCalls = result.stats.tools.byName;
```

### Use Cases
- Extracting specific data from responses
- Monitoring token usage
- Tracking tool call success/failure
- Building automation pipelines

## Pattern 3: Background Execution

For long-running tasks, execute in background and continue working.

```bash
# Start in background
gemini --model gemini-3-pro-preview "[long task]" --yolo --output-format text > /tmp/gemini-long.txt 2>&1 &

# Get process ID for later
echo $!

# Monitor output by reading /tmp/gemini-long.txt
```

### When to Use
- Code generation for large projects
- Documentation generation
- Running multiple Gemini tasks in parallel

### Parallel Execution
```bash
# Run multiple tasks simultaneously
gemini --model gemini-3-pro-preview "Create frontend" --yolo --output-format text > /tmp/gemini-frontend.txt 2>&1 &
gemini --model gemini-3-pro-preview "Create backend" --yolo --output-format text > /tmp/gemini-backend.txt 2>&1 &
gemini --model gemini-3-pro-preview "Create tests" --yolo --output-format text > /tmp/gemini-tests.txt 2>&1 &
```

## Pattern 4: Rate Limit Handling

Strategies for working within rate limits.

### Approach 1: Let Auto-Retry Handle It
Default behavior - CLI retries automatically with backoff.

### Approach 2: Use Flash for Lower Priority
```bash
# High priority: Use Pro
gemini --model gemini-3-pro-preview "[important task]" --yolo --output-format text

# Lower priority: keep using defaults; rely on auto-retry/backoff
gemini --model gemini-3-pro-preview "[less critical task]" --output-format text
```

### Approach 3: Batch Operations
Combine related operations into single prompts:
```bash
# Instead of multiple calls:
gemini --model gemini-3-pro-preview "Create file A" --yolo --output-format text
gemini --model gemini-3-pro-preview "Create file B" --yolo --output-format text
gemini --model gemini-3-pro-preview "Create file C" --yolo --output-format text

# Single call:
gemini --model gemini-3-pro-preview "Create files A, B, and C with [specs]. Create all now." --yolo --output-format text
```

### Approach 4: Sequential with Delays
For automated scripts, add delays:
```bash
gemini --model gemini-3-pro-preview "[task 1]" --yolo --output-format text
sleep 2
gemini --model gemini-3-pro-preview "[task 2]" --yolo --output-format text
```

## Pattern 5: Context Enrichment

Provide rich context for better results.

### Using File References
```bash
gemini --model gemini-3-pro-preview "Based on @./package.json and @./src/index.js, suggest improvements" --output-format text
```

### Using GEMINI.md
Create project context that's automatically included:
```markdown
# .gemini/GEMINI.md

## Project Overview
This is a React app using TypeScript.

## Coding Standards
- Use functional components
- Prefer hooks over classes
- All functions need JSDoc
```

### Explicit Context in Prompt
```bash
gemini --model gemini-3-pro-preview $'Given this context:\n- Project uses React 18 with TypeScript\n- State management: Zustand\n- Styling: Tailwind CSS\n\nCreate a user profile component.' --yolo --output-format text
```

## Pattern 6: Validation Pipeline

Always validate Gemini's output before using.

### Validation Steps

1. **Syntax Check**
   ```bash
   # For JavaScript
   node --check generated.js

   # For TypeScript
   tsc --noEmit generated.ts
   ```

2. **Security Scan**
   - Check for innerHTML with user input (XSS)
   - Look for eval() or Function() calls
   - Verify input validation

3. **Functional Test**
   - Run any generated tests
   - Manual smoke test

4. **Style Check**
   ```bash
   eslint generated.js
   prettier --check generated.js
   ```

### Automated Validation Pattern
```bash
# Generate
gemini --model gemini-3-pro-preview "Create utility functions" --yolo --output-format text

# Validate
node --check utils.js && eslint utils.js && npm test
```

## Pattern 7: Incremental Refinement

Build complex outputs in stages.

```bash
# Stage 1: Core structure
gemini --model gemini-3-pro-preview "Create basic Express server with routes for /api/users" --yolo --output-format text

# Stage 2: Add feature
gemini --model gemini-3-pro-preview "Add authentication middleware to the Express server in @server.js" --yolo --output-format text

# Stage 3: Add another feature
gemini --model gemini-3-pro-preview "Add rate limiting to the Express server in @server.js" --yolo --output-format text

# Stage 4: Review all
gemini --model gemini-3-pro-preview "Review @server.js for issues and optimize" --output-format text
```

### Benefits
- Easier to debug issues
- Each stage validates before continuing
- Clear audit trail

## Pattern 8: Cross-Validation with Claude

Use both AIs for highest quality.

### Claude Generates, Gemini Reviews
```bash
# 1. Claude writes code (using normal Claude Code tools)
# 2. Gemini reviews
gemini --model gemini-3-pro-preview "Review this code for bugs and security issues: [paste code]" --output-format text
```

### Gemini Generates, Claude Reviews
```bash
# 1. Gemini generates
gemini --model gemini-3-pro-preview "Create [code]" --yolo --output-format text

# 2. Claude reviews the output (in conversation)
# "Review this code that Gemini generated..."
```

### Different Perspectives
- Claude: Strong on reasoning, following complex instructions
- Gemini: Strong on current web knowledge, codebase investigation

## Pattern 9: Session Continuity

Use sessions for multi-turn workflows.

```bash
# Initial task
gemini --model gemini-3-pro-preview "Analyze this codebase architecture. Use @./ to read relevant files." --output-format text

# For multi-turn continuity, prefer interactive commands like /resume and /chat
# inside the `gemini` REPL (run `gemini` then type `/help` to discover commands).
```

### Use Cases
- Iterative analysis
- Building on previous context
- Debugging sessions

## Anti-Patterns to Avoid

### Don't: Expect Immediate Execution
YOLO mode doesn't prevent planning. Gemini may still present plans.

**Do**: Use forceful language ("Apply now", "Start immediately")

### Don't: Ignore Rate Limits
Hammering the API wastes time on retries.

**Do**: Use appropriate models, batch operations

### Don't: Trust Output Blindly
Gemini can make mistakes, especially with security.

**Do**: Always validate generated code

### Don't: Over-Specify in Single Prompt
Extremely long prompts can confuse the model.

**Do**: Use incremental refinement for complex tasks

### Don't: Forget Context Limits
Even with 1M tokens, context can overflow.

**Do**: Use .geminiignore, be specific about files
