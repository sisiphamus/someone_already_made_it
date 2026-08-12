# Agent notes

Find whether a tool, product, repo, or company already solves the user's problem.

## Flow

1. `sami clarify "..."` or MCP `clarify_problem`. Ask the returned questions if slots are empty.
2. `sami discover` / `discover_solutions` with job, pain, platform, constraints, tried filled. Leave competitive closure on unless they want consensus only.
3. Show strong hits, partial, ghost/low-fame, and the closure name list. Never say "nothing exists."

## Category lists

`sami category "vector database"` or `list_category`. Seeds the category, then expands every name (alternatives / vs / competitors) until a full round adds zero or the query budget hits. If budget hit, say the list is open.

## Don't

- Ship a top-10 listicle as complete
- Invent funding rounds or products
- Skip clarify on vague asks

## Quick commands

| Intent | Command |
|--------|---------|
| Backends | `sami doctor` |
| Questions | `sami clarify "..."` |
| Hunt | `sami discover "..." --job ... --pain ...` |
| Category | `sami category "..."` |
| Interactive | `sami ask "..."` |
