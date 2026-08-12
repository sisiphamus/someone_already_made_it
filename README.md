```
   _________  ____ ___  ___  ____  ____  ___ 
  / ___/ __ \/ __ `__ \/ _ \/ __ \/ __ \/ _ \
 (__  ) /_/ / / / / / /  __/ /_/ / / / /  __/
/____/\____/_/ /_/ /_/\___/\____/_/ /_/\___/ 
         __                    __     
  ____ _/ /_______  ____ _____/ /_  __
 / __ `/ / ___/ _ \/ __ `/ __  / / / /
/ /_/ / / /  /  __/ /_/ / /_/ / /_/ / 
\__,_/_/_/   \___/\__,_/\__,_/\__, /  
                             /____/   
                        __          _ __ 
   ____ ___  ____ _____/ /__       (_) /_
  / __ `__ \/ __ `/ __  / _ \     / / __/
 / / / / / / /_/ / /_/ /  __/    / / /_  
/_/ /_/ /_/\__,_/\__,_/\___/____/_/\__/  
                          /_____/        
```

![banner](assets/banner.jpg)

# someone_already_made_it

Most problems already have a tool, a repo, or a company attached. Search and agents return the famous ones. This finds the rest: peers of the big brands, thin-footprint products, low-star GitHub, early-stage stuff that only shows up under "X alternatives."

CLI, MCP, and an agent skill. MIT.

## Install

```bash
git clone https://github.com/sisiphamus/someone_already_made_it.git
cd someone_already_made_it
python3 -m venv .venv && .venv/bin/pip install -e .
```

Need at least one backend:

| Backend | Setup |
|---------|--------|
| Web | `export TAVILY_API_KEY=...` |
| GitHub | `gh` installed + `gh auth login` |

```bash
.venv/bin/sami doctor
```

## Use

```bash
.venv/bin/sami clarify "I don't like Notion"
.venv/bin/sami ask "organize my day without feeds eating it"
.venv/bin/sami discover "offline music I own" \
  --job "download bought albums in browser" \
  --pain "streaming only" \
  --platform "browser linux" \
  --tried "spotify free"

.venv/bin/sami category "web search API for AI agents"
.venv/bin/sami category "vector database" --domain "vector search"
```

`someone-already-made-it` and `sami` are the same binary.

## How it works

1. **Clarify** (up to 5 questions)
2. **Hunt** web + GitHub (incl. low-star)
3. **Competitive closure**: every name found gets alternatives / vs / competitors / switched from until a round adds nothing (or budget runs out)

Does not prove nothing exists. Only reports what turned up.

## MCP

```bash
.venv/bin/python -m someone_already_made_it.mcp_server
```

```json
{
  "mcpServers": {
    "someone-already-made-it": {
      "command": "/path/to/someone_already_made_it/.venv/bin/python",
      "args": ["-m", "someone_already_made_it.mcp_server"],
      "env": { "TAVILY_API_KEY": "tvly-..." }
    }
  }
}
```

Tools: `doctor`, `clarify_problem`, `discover_solutions`, `list_category`

## Agent hosts

Point the agent at [`AGENTS.md`](AGENTS.md) and [`skills/someone-already-made-it/SKILL.md`](skills/someone-already-made-it/SKILL.md).

## Tests

```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q
```

## License

MIT
