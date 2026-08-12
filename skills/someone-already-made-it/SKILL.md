---
name: someone-already-made-it
description: >
  Find existing tools, products, repos, and companies that solve a problem.
  Use for "has someone built X", alternatives, prior art for products, startup/tool discovery.
---

# someone_already_made_it

## Setup

```bash
pip install -e /path/to/someone_already_made_it
export TAVILY_API_KEY=...
gh auth login   # optional, for GitHub lane
sami doctor
```

## Steps

1. **Clarify**
   ```bash
   sami clarify "USER PROBLEM"
   ```
   Ask the user the questions. Fill job / pain / platform / constraints / tried.

2. **Discover** (closure on by default)
   ```bash
   sami discover "USER PROBLEM" \
     --job "..." --pain "..." --platform "..." \
     --constraints "..." --tried "..."
   ```

3. **Category map** (optional)
   ```bash
   sami category "vector database" --domain "vector search"
   ```

## Closure rule

For every tool name found, expand alternatives / vs / competitors until a full round adds nothing (or budget). The CLI does this when closure is enabled. Do not stop after one listicle.

## MCP

`doctor` · `clarify_problem` · `discover_solutions` · `list_category`

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
