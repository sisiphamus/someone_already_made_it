---
name: someone-already-made-it
description: >
  Find existing tools, products, GitHub repos, and companies that already solve a problem.
  Use when the user asks "has someone built X", "alternatives to", "find tools for",
  "what exists for", prior art for products, or discovery of software/startups including early-stage.
---

# someone_already_made_it

## When to use

User wants existing solutions — not to invent from zero. Includes long-tail / early-stage, not only consensus.

## Prerequisites

```bash
pip install -e /path/to/someone_already_made_it
# or: uv pip install -e .
export TAVILY_API_KEY=...   # web lane
gh auth login               # GitHub lane (optional but recommended)
sami doctor
```

## Agent workflow (do not skip)

1. **Clarify** (max 5 questions) before searching:
   ```bash
   sami clarify "USER PROBLEM"
   ```
   Or MCP: `clarify_problem`.
   Ask the user; fill job / pain / platform / constraints / tried.

2. **Discover** with competitive closure (default on):
   ```bash
   sami discover "USER PROBLEM" \
     --job "..." --pain "..." --platform "..." \
     --constraints "..." --tried "..."
   ```
   Or MCP: `discover_solutions`.

3. **Category lists** (e.g. all vector DBs / agent browsers):
   ```bash
   sami category "vector database" --domain "vector search"
   ```
   Or MCP: `list_category`.

## Meta rule (must)

After any list of tools/companies: for **every** name, expand alternatives/vs/competitors until a full round adds nothing (or budget). The CLI/MCP does this when closure is enabled. **Do not** stop after one “top 10” listicle.

## Output to the user

- Strong / partial / ghost matches with URLs  
- Closure tool list (peers of famous brands)  
- Never claim “nothing exists” — only “not found in searched sources”

## MCP config example

```json
{
  "mcpServers": {
    "someone-already-made-it": {
      "command": "python",
      "args": ["-m", "someone_already_made_it.mcp_server"],
      "env": { "TAVILY_API_KEY": "${TAVILY_API_KEY}" }
    }
  }
}
```

Or: `uv run --directory /path/to/repo python -m someone_already_made_it.mcp_server`
