---
name: architecture-layer-violation
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: '/src/core/.*\.ts$'
  - field: new_text
    operator: regex_match
    pattern: "from\\s+['\"]@?infrastructure|from\\s+['\"].*prisma|import.*PrismaService|import.*Controller"
action: block
---

**BLOCKED: Infrastructure import in Core layer**

Core layer cannot import from Infrastructure. Use port interface instead:

```typescript
// Create interface in src/core/.../ports/
export interface IUserRepository {
  findById(id: string): Promise<User | null>;
}

// Inject interface, not implementation
constructor(private readonly userRepo: IUserRepository) {}
```

Do NOT import PrismaService, Controllers, or @infrastructure in core files.
