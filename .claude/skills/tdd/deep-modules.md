# Deep Modules

> **Upstream**: Adapted from [mattpocock/skills/tdd/deep-modules.md](https://github.com/mattpocock/skills/blob/main/tdd/deep-modules.md). For the full architectural vocabulary see `../architecture-language/LANGUAGE.md`.

From Ousterhout's *A Philosophy of Software Design*:

**Deep module** = small interface + lots of implementation

```
┌─────────────────────┐
│   Small Interface   │  ← Few methods, simple params
├─────────────────────┤
│                     │
│                     │
│  Deep Implementation│  ← Complex logic hidden
│                     │
│                     │
└─────────────────────┘
```

**Shallow module** = large interface + little implementation (avoid)

```
┌─────────────────────────────────┐
│       Large Interface           │  ← Many methods, complex params
├─────────────────────────────────┤
│  Thin Implementation            │  ← Just passes through
└─────────────────────────────────┘
```

When designing interfaces, ask:

- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?

For finding shallow modules already in the codebase and turning them into deep ones, use the `/improve-codebase-architecture` skill.
