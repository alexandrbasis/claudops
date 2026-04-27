---
name: ubiquitous-language
description: >-
  Extract a DDD-style ubiquitous language glossary from the current
  conversation, flagging ambiguities and proposing canonical terms. Saves to
  product-docs/UBIQUITOUS_LANGUAGE.md. Use when user wants to define domain
  terms, build a glossary, harden terminology, or mentions "domain model" or
  "DDD". Also invoked from /nf, /product, /ct as Step 0 (load) and after grill
  (update). NOT for architectural vocabulary (use /architecture-language).
---

# Ubiquitous Language

> **Upstream**: Adapted from [mattpocock/skills/ubiquitous-language](https://github.com/mattpocock/skills/blob/main/ubiquitous-language/SKILL.md). Concept from Eric Evans, *Domain-Driven Design*.

Extract and formalize domain terminology from the current conversation into a consistent glossary stored at `product-docs/UBIQUITOUS_LANGUAGE.md`. The same vocabulary is used by domain experts, the user, and the AI — both in planning docs (PRD, JTBD, discovery, tech-decomposition) and in code.

## When this fires

- **`/nf` Step 0**: load existing glossary so discovery questions and the discovery doc use canonical terms.
- **`/nf` Step 4 → Step 5 transition**: after the grill round, update glossary with new terms before writing the discovery doc.
- **`/product` Step 0** and **after Step 4 grill**: same pattern — load before interview, update before writing PRD/JTBD.
- **`/ct` GATE 1**: load alongside discovery/PRD docs so decomposition aligns with project terms.
- **Manual invocation**: any time the user asks to harden terminology or names a term that needs disambiguation.

## Process

1. **Read existing glossary** at `product-docs/UBIQUITOUS_LANGUAGE.md` (if it exists). Hold its content in memory — do NOT use Edit/section-patching. The file is small; the safe path is read → merge in memory → overwrite.
2. **Scan the relevant scope** for domain-relevant nouns, verbs, and concepts:
   - Current conversation
   - The active task's PRD / JTBD / discovery doc
   - Source code only when terms are ambiguous and the code resolves them
3. **Identify problems**:
   - Same word used for different concepts (ambiguity)
   - Different words used for the same concept (synonyms)
   - Vague or overloaded terms
4. **Merge in memory**: combine existing entries with new findings. Preserve every existing term unless evidence shows it's wrong; revise definitions that have sharpened. Add newly discovered terms. Update "Flagged ambiguities" with anything resolved.
5. **Ensure parent directory exists** before writing: `mkdir -p product-docs/` (the directory is repo-level, alongside `.claude/`, and may not exist on a fresh repo).
6. **Write the full merged glossary** to `product-docs/UBIQUITOUS_LANGUAGE.md`, fully overwriting the prior file.
7. **Output a summary** inline so the caller (`/nf`, `/product`, `/ct`) can paste it into its doc.

## Output format

`product-docs/UBIQUITOUS_LANGUAGE.md`:

```md
# Ubiquitous Language

> Domain terms used across PRDs, JTBDs, discovery docs, tech-decompositions, and code. Update via the `/ubiquitous-language` skill — auto-invoked from `/nf`, `/product`, `/ct`.

## [Subdomain or lifecycle name]

| Term        | Definition                                              | Aliases to avoid      |
| ----------- | ------------------------------------------------------- | --------------------- |
| **Order**   | A customer's request to purchase one or more items      | Purchase, transaction |
| **Invoice** | A request for payment sent after delivery               | Bill, payment request |

## People

| Term         | Definition                                  | Aliases to avoid       |
| ------------ | ------------------------------------------- | ---------------------- |
| **Customer** | A person or organization that places orders | Client, buyer, account |
| **User**     | An authentication identity in the system    | Login, account         |

## Relationships

- An **Invoice** belongs to exactly one **Customer**
- An **Order** produces one or more **Invoices**

## Example dialogue

> **Dev:** "When a **Customer** places an **Order**, do we create the **Invoice** immediately?"
> **Domain expert:** "No — an **Invoice** is only generated once a **Fulfillment** is confirmed."

## Flagged ambiguities

- "account" was used to mean both **Customer** and **User** — these are distinct: a **Customer** places orders, while a **User** is an authentication identity.
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick one and list the others as aliases to avoid.
- **Flag conflicts explicitly.** If a term is used ambiguously, call it out in "Flagged ambiguities" with a recommendation.
- **Only domain terms.** Skip generic programming concepts (array, function, endpoint) and skip the names of modules or classes unless they have meaning in the domain language.
- **Tight definitions.** One sentence max. Define what it IS, not what it does.
- **Show relationships.** Use bold term names; express cardinality where obvious.
- **Group into multiple tables** when natural clusters emerge (subdomain, lifecycle, actor). One table is fine if the domain is cohesive.
- **Write an example dialogue.** A short conversation (3-5 exchanges) between a dev and a domain expert that uses the terms precisely. The dialogue clarifies boundaries between related concepts.
- **No file paths or code snippets.** This is a domain document, not an implementation reference.

## Re-running

When invoked again in the same conversation:

1. Read existing `UBIQUITOUS_LANGUAGE.md`
2. Incorporate new terms from subsequent discussion
3. Update definitions if understanding has evolved
4. Re-flag any new ambiguities
5. Rewrite the example dialogue to incorporate new terms

## Return to caller

After writing/updating the file, return a compact summary so `/nf`, `/product`, or `/ct` can reference it without re-reading the file:

- Terms added: [list]
- Terms revised: [list]
- Ambiguities flagged: [list]
- Suggested canonical phrasing for the upcoming doc: [1-3 examples]
