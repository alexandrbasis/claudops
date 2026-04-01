# Contributing to Claude Code Workflows

Thank you for your interest in contributing to this project! This repository showcases Claude Code workflows used in production, and we welcome improvements, bug fixes, and new workflow patterns.

## How to Contribute

### Reporting Issues

If you find a bug, have a question, or want to suggest an improvement:

1. Check [existing issues](https://github.com/alexandrbasis/claudops/issues) to avoid duplicates
2. Create a new issue with:
   - Clear, descriptive title
   - Detailed description of the problem or suggestion
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (OS, Claude Code version, Python version)

### Suggesting Enhancements

We love new ideas! To suggest an enhancement:

1. Open an issue with the label `enhancement`
2. Describe the enhancement clearly:
   - What problem does it solve?
   - How would it work?
   - What are the benefits?
   - Any potential drawbacks?

### Contributing Code

#### Before You Start

1. **Check existing work** - Look at open issues and PRs to avoid duplicates
2. **Discuss first** - For major changes, open an issue first to discuss the approach
3. **Small PRs** - Break large changes into smaller, focused PRs

#### Development Process

1. **Fork the repository**
   ```bash
   gh repo fork alexandrbasis/claudops --clone
   cd claudops
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments where necessary
   - Update documentation if needed

4. **Test your changes**
   - Test agents, skills, and hooks locally
   - Ensure no sensitive data is included
   - Verify hook logs for errors

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

6. **Push and create a PR**
   ```bash
   git push origin feature/your-feature-name
   gh pr create --title "feat: your feature title" --body "Description of changes"
   ```

#### Pull Request Guidelines

**Good PR characteristics:**
- Focused on a single change or feature
- Includes clear description of what and why
- Updates documentation if needed
- Follows existing code patterns
- No sensitive data (tokens, IDs, personal info)

**PR Template:**
```markdown
## Description
Brief description of what this PR does

## Motivation
Why is this change needed?

## Changes
- Change 1
- Change 2

## Testing
How was this tested?

## Checklist
- [ ] Code follows existing style
- [ ] Documentation updated
- [ ] No sensitive data included
- [ ] Tested locally
```

### Contributing Workflow Ideas

Have a cool workflow pattern? Share it!

**What we're looking for:**
- Novel agent configurations
- Useful hook automations
- Helpful skills and workflows
- Productivity tips
- Integration patterns

**How to share:**
1. Create an issue describing the workflow
2. Submit a PR with the implementation
3. Include documentation on how to use it
4. Share examples of how it helps

## Code Style

### Python (Hooks)

- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to functions
- Keep functions focused and small
- Handle errors gracefully

```python
def example_function(param: str) -> bool:
    """
    Brief description of what function does

    Args:
        param: Description of parameter

    Returns:
        Description of return value
    """
    # Implementation
    return True
```

### Bash (Scripts)

- Use `set -e` for error handling
- Quote variables: `"$VAR"`
- Add comments for complex logic
- Use functions for reusability

```bash
#!/bin/bash
set -e

# Description of what script does
main() {
    local var="value"
    echo "Processing: $var"
}

main "$@"
```

### Markdown (Agents, Commands, Docs)

- Clear, descriptive headings
- Use code blocks with language tags
- Include examples where helpful
- Keep line length reasonable (80-120 chars)

## Security Guidelines

**Never commit:**
- API keys or tokens
- Personal IDs (Telegram, Linear, etc.)
- Passwords or credentials
- Internal URLs or IPs
- Personal file paths (use `$HOME`, `$CLAUDE_PROJECT_DIR`)

**Always:**
- Use template files for configuration
- Add sensitive files to `.gitignore`
- Sanitize examples and screenshots
- Review diffs before committing

## Documentation

When adding features:

1. **Update README** - If it affects main functionality
2. **Update setup-guide.md** - If it requires configuration
3. **Add inline comments** - For complex logic
4. **Create examples** - Show how to use it

## Testing

Before submitting:

1. **Test locally** - Run the workflow in your environment
2. **Check logs** - Review hook-debug.log for errors
3. **Test edge cases** - What happens when it fails?
4. **Verify exclusions** - Ensure no sensitive data is included

## Community

- Be respectful and constructive
- Help others learn
- Share knowledge
- Give credit where due

## Questions?

- **General questions**: Open a [Discussion](https://github.com/alexandrbasis/claudops/discussions)
- **Bug reports**: Open an [Issue](https://github.com/alexandrbasis/claudops/issues)
- **Feature ideas**: Open an [Issue](https://github.com/alexandrbasis/claudops/issues) with `enhancement` label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to these Claude Code workflows!
