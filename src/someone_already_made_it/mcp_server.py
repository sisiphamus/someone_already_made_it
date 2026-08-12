"""MCP server: someone_already_made_it

Tools for agent hosts (Claude Code, Cursor, Grok, etc.):
  - clarify_problem
  - discover_solutions
  - list_category (competitive closure)
  - doctor
"""

from __future__ import annotations

import json
from typing import Any

from .clarify import plan_clarify
from .closure import competitive_closure
from .env import load_env
from .hunt import HuntSlots, render_markdown, run_hunt
from .sources import has_github, has_web


def _doctor() -> str:
    load_env()
    return json.dumps(
        {
            "tavily": has_web(),
            "github_gh": has_github(),
            "ok": has_web() or has_github(),
        }
    )


def main() -> None:
    load_env()
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        # fallback older mcp
        from mcp.server.fastmcp import FastMCP  # type: ignore

    mcp = FastMCP("someone_already_made_it")

    @mcp.tool()
    def doctor() -> str:
        """Check whether Tavily and/or GitHub (gh) search backends are configured."""
        return _doctor()

    @mcp.tool()
    def clarify_problem(problem: str) -> str:
        """Given a user problem in plain language, return up to 5 refining questions to ask before searching."""
        return json.dumps(plan_clarify(problem), indent=2)

    @mcp.tool()
    def discover_solutions(
        problem: str,
        job: str = "",
        pain: str = "",
        platform: str = "",
        constraints: str = "",
        tried: str = "",
        max_queries: int = 10,
        with_closure: bool = True,
        early_stage: bool = True,
        as_markdown: bool = True,
    ) -> str:
        """Find tools, products, repos, and companies that may already solve the problem.

        Prefer calling clarify_problem first and filling job/pain/platform/constraints/tried.
        Uses multi-lane search + competitive closure (alternatives/vs for every name found).
        """
        load_env()
        if not has_web() and not has_github():
            return "ERROR: set TAVILY_API_KEY and/or run `gh auth login`."
        slots = HuntSlots(
            problem=problem,
            job=job,
            pain=pain,
            platform=platform,
            constraints=constraints,
            tried=tried,
        )
        report = run_hunt(
            slots,
            max_queries=max_queries,
            early_stage=early_stage,
            with_closure=with_closure,
        )
        if as_markdown:
            return render_markdown(report)
        return json.dumps(report, indent=2, default=str)

    @mcp.tool()
    def list_category(
        category: str,
        domain_phrase: str = "",
        max_tools: int = 40,
        max_queries: int = 45,
        early_stage: bool = True,
    ) -> str:
        """List tools in a category using competitive closure until fixed point (or budget cap).

        Example category: "vector database", "web search API for AI agents".
        """
        load_env()
        if not has_web() and not has_github():
            return "ERROR: set TAVILY_API_KEY and/or run `gh auth login`."
        seeds = [
            f"{category} tools",
            f"{category} software",
            f"{category} open source",
            f"best {category}",
            f"{category} API",
        ]
        cr = competitive_closure(
            seeds,
            domain_phrase=domain_phrase or category,
            max_tools=max_tools,
            max_queries=max_queries,
            early_stage=early_stage,
        )
        return json.dumps(
            {
                "category": category,
                "tools": cr.tools,
                "overflow": cr.overflow,
                "closure_log": cr.closure_log,
                "stop_reason": cr.stop_reason,
                "queries_run": cr.queries_run,
                "closed": cr.closed,
            },
            indent=2,
            default=str,
        )

    mcp.run()


if __name__ == "__main__":
    main()
