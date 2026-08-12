# Agent instructions — someone_already_made_it

You are using **someone_already_made_it** to find whether tools, products, repos, or companies already solve the user's problem.

## Required method

1. Call **clarify** (CLI or MCP) and ask the user the returned questions (skip slots already answered).
2. Call **discover** with filled slots. Keep **competitive closure** enabled unless the user wants a quick consensus-only scan.
3. Present: strong matches, partial, ghost/low-fame, and the closure peer list.
4. Never certify absence. Say what was searched.

## Competitive closure (always for lists)

For category enumeration (`list_category` / `sami category`): seed category queries, then for every name found search alternatives/vs/competitors/switched from/better than — until a full round adds zero new names (or budget cap; then say not closed).

## Do not

- Return only SEO “best of 2026” without closure  
- Invent companies or funding rounds  
- Skip clarify when the problem is vague (“I need better productivity”)

## Commands

| Intent | Command |
|--------|---------|
| Check backends | `sami doctor` |
| Questions | `sami clarify "..."` |
| Full hunt | `sami discover "..." --job ... --pain ...` |
| Category map | `sami category "vector database"` |
| Interactive | `sami ask "..."` |
