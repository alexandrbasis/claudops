# Gemini CLI Prompt Templates

Reusable prompt templates for common operations.

## One-shot prompt rule (critical)

`gemini "..."` is a **one-shot** call by default. There is no back-and-forth unless you explicitly start an interactive session (`gemini` REPL or `-i/--prompt-interactive`).

So prompts must be **complete**: include inputs (`@path`), constraints, and the exact deliverable.

## Code Generation

### Single-File Application
```bash
gemini --model gemini-3-pro-preview "Create a [description] with [features]. Include [requirements]. Output the complete file content." --yolo --output-format text
```

**Example:**
```bash
gemini --model gemini-3-pro-preview "Create a single-file HTML/CSS/JS calculator with: basic operations, history display, keyboard support, dark mode toggle, responsive design. Output the complete file content." --yolo --output-format text
```

### Multi-File Project
```bash
gemini --model gemini-3-pro-preview "Create a [project type] with [stack]. Include [features]. Create all necessary files and make it runnable. Use modern best practices. START BUILDING NOW." --yolo --output-format text
```

**Example:**
```bash
gemini --model gemini-3-pro-preview "Create a REST API with Express, SQLite, and JWT auth. Include user CRUD, input validation, error handling. Create all necessary files and make it runnable. START BUILDING NOW." --yolo --output-format text
```

### Component/Module
```bash
gemini --model gemini-3-pro-preview "Create a [component type] that [functionality]. Follow [standards]. Include [requirements]. Output the code." --yolo --output-format text
```

**Example:**
```bash
gemini --model gemini-3-pro-preview "Create a React hook useLocalStorage that syncs state with localStorage. Follow React 18 best practices. Include TypeScript types. Output the code." --yolo --output-format text
```

## Code Review

### Comprehensive Review
```bash
gemini --model gemini-3-pro-preview $'Review @path/to/file and tell me:\n1) What features it has\n2) Any bugs or security issues\n3) Suggestions for improvement\n4) Code quality assessment' --output-format text
```

### Security-Focused Review
```bash
gemini --model gemini-3-pro-preview $'Review @path/to/file for security vulnerabilities including:\n- XSS (cross-site scripting)\n- SQL injection\n- Command injection\n- Insecure data handling\n- Authentication issues\nReport findings with severity levels.' --output-format text
```

### Performance Review
```bash
gemini --model gemini-3-pro-preview $'Analyze @path/to/file for performance issues:\n- Inefficient algorithms\n- Memory leaks\n- Unnecessary re-renders\n- Blocking operations\n- Optimization opportunities\nProvide specific recommendations.' --output-format text
```

## Bug Fixing

### Fix Identified Bugs
```bash
gemini --model gemini-3-pro-preview $'Fix these bugs in @path/to/file:\n1) [Bug description]\n2) [Bug description]\n3) [Bug description]\nApply fixes now.' --yolo --output-format text
```

### Auto-Detect and Fix
```bash
gemini --model gemini-3-pro-preview "Analyze @path/to/file for bugs, then fix all issues you find. Apply fixes immediately." --yolo --output-format text
```

## Test Generation

### Unit Tests
```bash
gemini --model gemini-3-pro-preview $'Generate [framework] unit tests for @path/to/file. Cover:\n- All public functions\n- Edge cases\n- Error handling\n- [Specific areas]\nOutput the complete test file.' --yolo --output-format text
```

**Example:**
```bash
gemini --model gemini-3-pro-preview $'Generate Jest unit tests for @utils.js. Cover:\n- All exported functions\n- Edge cases (empty input, null, undefined)\n- Error handling\n- Boundary conditions\nOutput the complete test file.' --yolo --output-format text
```

### Integration Tests
```bash
gemini --model gemini-3-pro-preview $'Generate integration tests for [component/API]. Test:\n- Happy path scenarios\n- Error scenarios\n- Edge cases\nUse [framework]. Output complete test file.' --yolo --output-format text
```

## Documentation

### JSDoc/TSDoc
```bash
gemini --model gemini-3-pro-preview $'Generate [JSDoc/TSDoc] documentation for all functions in @path/to/file. Include:\n- Function descriptions\n- Parameter types and descriptions\n- Return types and descriptions\n- Usage examples\nOutput as [format].' --yolo --output-format text
```

### README Generation
```bash
gemini --model gemini-3-pro-preview $'Generate a README.md for this project. Include:\n- Project description\n- Installation instructions\n- Usage examples\n- API reference\n- Contributing guidelines\nUse the codebase to gather accurate information. Use @./ to read the project.' --yolo --output-format text
```

### API Documentation
```bash
gemini --model gemini-3-pro-preview $'Document all API endpoints in @path/to/file_or_directory. Include:\n- HTTP method and path\n- Request parameters\n- Request body schema\n- Response schema\n- Example requests/responses\nOutput in [Markdown/OpenAPI] format.' --yolo --output-format text
```

## Code Transformation

### Refactoring
```bash
gemini --model gemini-3-pro-preview $'Refactor @path/to/file to:\n- [Specific improvement]\n- [Specific improvement]\nMaintain all existing functionality. Apply changes now.' --yolo --output-format text
```

### Language Translation
```bash
gemini --model gemini-3-pro-preview $'Translate @path/to/file from [source language] to [target language]. Maintain:\n- Same functionality\n- Similar code structure\n- Idiomatic patterns for target language\nOutput the translated code.' --yolo --output-format text
```

### Framework Migration
```bash
gemini --model gemini-3-pro-preview "Convert @path/to/file from [old framework] to [new framework]. Maintain all functionality. Use [new framework] best practices. Output the converted code." --yolo --output-format text
```

## Web Research

### Current Information
```bash
gemini --model gemini-3-pro-preview "What are the latest [topic] as of [date]? Use Google Search to find current information. Summarize key points." --output-format text
```

### Library/API Research
```bash
gemini --model gemini-3-pro-preview $'Research [library/API] and provide:\n- Latest version and changes\n- Best practices\n- Common patterns\n- Gotchas to avoid\nUse Google Search for current information.' --output-format text
```

### Comparison Research
```bash
gemini --model gemini-3-pro-preview "Compare [option A] vs [option B] for [use case]. Use Google Search for current benchmarks and community opinions. Provide recommendation." --output-format text
```

## Architecture Analysis

### Project Analysis
```bash
gemini --model gemini-3-pro-preview $'Analyze this project. Use @./ to read relevant files. Report on:\n- Overall architecture\n- Key dependencies\n- Component relationships\n- Potential issues' --output-format text
```

### Dependency Analysis
```bash
gemini --model gemini-3-pro-preview $'Analyze dependencies in this project:\n- Direct vs transitive\n- Outdated packages\n- Security vulnerabilities\n- Bundle size impact\nUse @./package.json and @./package-lock.json (or pnpm/yarn equivalents).' --output-format text
```

## Specialized Tasks

### Git Commit Message
```bash
gemini --model gemini-3-pro-preview "Analyze staged changes and generate a commit message. Be concise but descriptive." --output-format text
```

### Code Explanation
```bash
gemini --model gemini-3-pro-preview $'Explain what @path/to/file (or a function inside it) does in detail:\n- Purpose and use case\n- How it works step by step\n- Key algorithms/patterns used\n- Dependencies and side effects' --output-format text
```

### Error Diagnosis
```bash
gemini --model gemini-3-pro-preview $'Diagnose this error:\n[error message]\nContext: [relevant context]\nProvide:\n- Root cause\n- Solution steps\n- Prevention tips' --output-format text
```

## Template Variables

Use these placeholders in templates:

- `[file]` - File path or name
- `[directory]` - Directory path
- `[description]` - Brief description
- `[features]` - List of features
- `[requirements]` - Specific requirements
- `[framework]` - Testing/UI framework
- `[language]` - Programming language
- `[format]` - Output format (markdown, JSON, etc.)
- `[date]` - Date for time-sensitive queries
- `[topic]` - Subject matter for research
