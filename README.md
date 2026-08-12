# someone_already_made_it

**Someone already made it.** Find tools, products, GitHub repos, and companies that solve a problem — including peers of famous brands and early-stage options that one Google pass misses.

Built for **humans and coding agents** (CLI + MCP + agent skill).

## Why this exists

Normal search and agents return **consensus**. The thing you need is often:

- a Series A company with a thin website  
- a 12-star GitHub repo  
- the peer of Tavily that only shows up under “Tavily alternatives” (e.g. Linkup)

This project runs:

1. **Clarify** — up to 5 refining questions  
2. **Multi-lane hunt** — web (Tavily) + GitHub (`gh`), including low-star repos  
3. **Competitive closure** — for every name found, expand alternatives / vs / competitors until a full round adds nothing (or budget)

Validated meta: competitive closure finds peers that seed-only search misses.

## Install

```bash
git clone https://github.com/sisiphamus/someone_already_made_it.git
cd someone_already_made_it
pip install -e .
# or: uv pip install -e .
```

### Backends (at least one)

| Backend | Env / setup | Lane |
|---------|-------------|------|
| **Tavily** | `export TAVILY_API_KEY=tvly-...` | Web search |
| **GitHub** | [GitHub CLI](https://cli.github.com/) + `gh auth login` | Repos / ghosts |

```bash
sami doctor
```

## CLI

```bash
# Refining questions only
sami clarify "I don't like Notion"

# Full discovery (problem + slots)
sami discover "organize my day without getting distracted" \
  --job "plan 3 outcomes and execute" \
  --pain "feeds and procrastination" \
  --platform "linux laptop and phone" \
  --constraints "stay in Obsidian if possible" \
  --tried "daily markdown files"

# Interactive
sami ask "I need offline music I own from the browser"

# Category map with competitive closure
sami category "web search API for AI agents" --domain "AI agents"
sami category "vector database" --domain "vector search"

# JSON
sami discover "..." --json --out report.json
sami category "vector database" --json
```

Aliases: `someone-already-made-it` or `sami`.

## MCP (Claude Code, Cursor, Grok, …)

```bash
# run server (stdio)
python -m someone_already_made_it.mcp_server
```

Example config:

```json
{
  "mcpServers": {
    "someone-already-made-it": {
      "command": "python",
      "args": ["-m", "someone_already_made_it.mcp_server"],
      "env": {
        "TAVILY_API_KEY": "tvly-..."
      }
    }
  }
}
```

**Tools:** `doctor` · `clarify_problem` · `discover_solutions` · `list_category`

## Agent skill

Copy or point your agent at:

[`skills/someone-already-made-it/SKILL.md`](skills/someone-already-made-it/SKILL.md)

Also see [`AGENTS.md`](AGENTS.md) for host-agnostic instructions.

## Method (short)

```
problem → clarify (≤5) → multi-lane search → competitive closure → report
```

**Competitive closure:** for every tool name found, query `{name} alternatives`, `{name} vs`, `competitors to {name}`, `switched from {name}`, `better than {name} for …` — repeat until fixed point.

Never certifies that nothing exists — only reports what was found in searched sources.

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```

## License

MIT
