# Refactor Candidates

> **Upstream**: Faithful copy from [mattpocock/skills/tdd/refactoring.md](https://github.com/mattpocock/skills/blob/main/tdd/refactoring.md).

After TDD cycle, look for:

- **Duplication** → Extract function/class
- **Long methods** → Break into private helpers (keep tests on public interface)
- **Shallow modules** → Combine or deepen (see `/improve-codebase-architecture`)
- **Feature envy** → Move logic to where data lives
- **Primitive obsession** → Introduce value objects
- **Existing code** the new code reveals as problematic
