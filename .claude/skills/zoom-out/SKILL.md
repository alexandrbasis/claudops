---
name: zoom-out
description: >-
  Step up one layer of abstraction and produce a map of the relevant modules
  and their callers — used when you (or the agent) are stuck in one file and
  losing the bigger picture. Use when user says "zoom out", "give me a map",
  "I'm lost in this code", or "what calls this".
disable-model-invocation: true
---

# Zoom Out

> **Upstream**: Adapted from [mattpocock/skills/zoom-out](https://github.com/mattpocock/skills/blob/main/zoom-out/SKILL.md).

Step out of the current file. Go up one layer of abstraction. Produce a compact map of:

- The **modules** in this area (use `architecture-language/LANGUAGE.md` vocabulary)
- Their **callers** — who reaches into this code and from where
- Their **dependencies** — what this code reaches into

Do not propose changes. Do not deep-dive into any one module. The point is to recover bearings, not to solve a problem.

If `product-docs/UBIQUITOUS_LANGUAGE.md` exists, name modules using its terms when possible.
