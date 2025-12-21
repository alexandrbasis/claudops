# Research Guidelines (Exa + Ref MCP)

## Priority Order
1. **Exa first**: `get_code_context_exa` for code-aware context
2. **Exa fallback**: `web_search_exa` for targeted top sources
3. **Ref last**: Only when Exa contradicts or docs suspected outdated

## Ref Usage Rules
- Use only `ref_search_documentation` for lookups
- Never use `search_docs` or `my_docs`
- Use `ref_read_url` for primary docs when:
  - User explicitly requests docs
  - Results would clarify Exa findings

## Operational Flow
1. Exa → `get_code_context_exa` (code-oriented query)
2. If insufficient → Exa → `web_search_exa`
3. If still stuck → Ref → `ref_search_documentation`
4. Annotate critical links/versions in code comments

## Best Practices
- Keep queries specific and focused
- Prefer multiple small queries over one broad query
- Use Ref sparingly (authoritative verification only)
