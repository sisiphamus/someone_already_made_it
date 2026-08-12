"""Competitive closure: expand every found name until fixed point."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from .extract import names_from_hit
from .sources import github_search_repos, tavily_search


SearchFn = Callable[[str, int], list[dict[str, Any]]]


@dataclass
class ClosureResult:
    tools: list[dict[str, Any]]  # {name, evidence: [hits], fame?}
    overflow: list[str]
    closure_log: list[dict[str, Any]]
    stop_reason: str
    queries_run: int
    closed: bool


def _default_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    hits = tavily_search(query, max_results=max_results)
    if any(k in query.lower() for k in ("github", "open source", "repo", "oss")):
        hits.extend(github_search_repos(query, limit=4))
    return hits


def expansion_queries(name: str, domain_phrase: str = "AI agents") -> list[str]:
    return [
        f"{name} alternatives",
        f"{name} vs",
        f"competitors to {name}",
        f"switched from {name}",
        f"better than {name} for {domain_phrase}",
    ]


def competitive_closure(
    seed_queries: list[str],
    *,
    domain_phrase: str = "AI agents",
    max_tools: int = 40,
    max_queries: int = 50,
    search: SearchFn | None = None,
    early_stage: bool = True,
) -> ClosureResult:
    """
    Seed category queries, then expand every name with competitor queries
    until a full round adds no new names (or caps hit).
    """
    search = search or _default_search
    tools: dict[str, dict[str, Any]] = {}
    overflow: list[str] = []
    log: list[dict[str, Any]] = []
    queries_run = 0
    pending_expand: list[str] = []
    expanded: set[str] = set()

    def add_name(name: str, hit: dict[str, Any] | None = None) -> bool:
        key = name.strip()
        if len(key) < 2:
            return False
        # skip pure noise
        if key.lower() in {"the", "and", "for", "with", "open", "source", "api"}:
            return False
        if key not in tools:
            if len(tools) >= max_tools:
                if key not in overflow:
                    overflow.append(key)
                return False
            tools[key] = {"name": key, "evidence": [], "sources": set()}
            pending_expand.append(key)
            is_new = True
        else:
            is_new = False
        if hit:
            tools[key]["evidence"].append(
                {
                    "title": hit.get("title"),
                    "url": hit.get("url"),
                    "snippet": (hit.get("content") or "")[:200],
                }
            )
            if hit.get("url"):
                tools[key]["sources"].add(hit["url"])
        return is_new

    def run_query(q: str) -> int:
        nonlocal queries_run
        if queries_run >= max_queries:
            return 0
        queries_run += 1
        hits = search(q, 5)
        time.sleep(0.12)
        new = 0
        for h in hits:
            for n in names_from_hit(h):
                if add_name(n, h):
                    new += 1
        return new

    # --- seeds ---
    seeds = list(seed_queries)
    if early_stage:
        seeds.extend(
            [
                f"{seed_queries[0]} seed startup" if seed_queries else "seed startup tool",
                f"{seed_queries[0]} Series A" if seed_queries else "Series A product",
                "Product Hunt " + (seed_queries[0] if seed_queries else "AI tool"),
            ]
        )
    seed_new = 0
    for q in seeds[:8]:
        seed_new += run_query(q)
    log.append({"seed": "category seeds", "new": seed_new, "queries": seeds[:8]})

    # --- closure rounds ---
    rounds = 0
    while pending_expand and queries_run < max_queries and rounds < 20:
        rounds += 1
        batch = [n for n in pending_expand if n not in expanded]
        pending_expand = []
        if not batch:
            break
        round_new = 0
        for name in batch:
            if queries_run >= max_queries:
                break
            expanded.add(name)
            for eq in expansion_queries(name, domain_phrase):
                if queries_run >= max_queries:
                    break
                round_new += run_query(eq)
        log.append(
            {
                "seed": f"closure round {rounds} ({len(batch)} names)",
                "new": round_new,
                "expanded": batch[:20],
            }
        )
        if round_new == 0 and not pending_expand:
            # fixed point
            return ClosureResult(
                tools=_finalize(tools),
                overflow=overflow,
                closure_log=log,
                stop_reason="fixed-point",
                queries_run=queries_run,
                closed=True,
            )

    reason = "fixed-point" if not pending_expand and rounds > 0 else "cap hit"
    if queries_run >= max_queries:
        reason = "cap hit"
    if len(tools) >= max_tools and pending_expand:
        reason = "cap hit"

    return ClosureResult(
        tools=_finalize(tools),
        overflow=overflow,
        closure_log=log,
        stop_reason=reason,
        queries_run=queries_run,
        closed=reason == "fixed-point",
    )


def _finalize(tools: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for t in tools.values():
        out.append(
            {
                "name": t["name"],
                "evidence": t["evidence"][:5],
                "urls": list(t["sources"])[:5],
                "evidence_count": len(t["evidence"]),
            }
        )
    out.sort(key=lambda x: (-x["evidence_count"], x["name"].lower()))
    return out


def seed_queries_for_problem(
    problem: str,
    job: str = "",
    pain: str = "",
    platform: str = "",
) -> list[str]:
    base = job or problem
    qs = [
        f"{base} tool software",
        f"{base} open source",
        f"{base} app alternative",
        f"best {base} for {platform}".strip() if platform else f"best {base} software",
    ]
    if pain:
        qs.append(f"{base} {pain}")
    # product leave mining
    return qs[:5]
