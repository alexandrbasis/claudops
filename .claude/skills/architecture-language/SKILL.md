---
name: architecture-language
description: >-
  Canonical architectural vocabulary — module, interface, seam, adapter, depth,
  leverage, locality. Use when reviewing architecture, deepening shallow modules,
  designing interfaces, or evaluating refactor candidates. NOT a domain glossary
  (use /ubiquitous-language for that).
disable-model-invocation: true
---

# Architecture Language

Shared vocabulary for every architectural conversation in this repo. Use these terms exactly — don't substitute "component", "service", "API", or "boundary". Consistent language is the whole point.

The full glossary lives in [LANGUAGE.md](LANGUAGE.md). Load it when:

- Reviewing architecture (`senior-architecture-reviewer`, `code-analysis`)
- Hunting deepening opportunities (`improve-codebase-architecture`)
- Designing interfaces or evaluating module shape
- TDD planning where module depth affects test surface

## Why this exists

A codebase full of shallow modules is hard for both humans and AI to navigate. The vocabulary in `LANGUAGE.md` makes the distinction between *deep* and *shallow* sayable, which is the prerequisite for fixing it.

When reviewing or planning, prefer the precise term over the casual one — say **seam**, not "boundary"; **interface**, not "API surface"; **adapter**, not "implementation of the interface".

## Upstream

The vocabulary and principles are adapted from Matt Pocock's `improve-codebase-architecture/LANGUAGE.md` ([github.com/mattpocock/skills](https://github.com/mattpocock/skills)), which itself draws on Ousterhout (*A Philosophy of Software Design*) and Feathers (*Working Effectively with Legacy Code*).
