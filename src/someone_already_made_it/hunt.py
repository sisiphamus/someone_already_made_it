from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass
from typing import Any

from .clarify import extract_mentioned_products
from .closure import competitive_closure, seed_queries_for_problem
from .sources import github_search_repos, tavily_search


@dataclass
class HuntSlots:
    problem: str
    job: str = ""
    pain: str = ""
    platform: str = ""
    constraints: str = ""
    tried: str = ""

    def products(self) -> list[str]:
        return extract_mentioned_products(
            " ".join([self.problem, self.job, self.pain, self.tried])
        )


def _score_hit(hit: dict[str, Any], slots: HuntSlots) -> dict[str, Any]:
    text = f"{hit.get('title','')} {hit.get('content','')} {hit.get('url','')}".lower()
    job_t = set(re.findall(r"[a-z0-9]{3,}", (slots.job or slots.problem).lower()))
    pain_t = set(re.findall(r"[a-z0-9]{3,}", slots.pain.lower())) if slots.pain else set()
    tokens = set(re.findall(r"[a-z0-9]{3,}", text))
    job_o = len(job_t & tokens) / max(1, len(job_t))
    pain_o = len(pain_t & tokens) / max(1, len(pain_t)) if pain_t else 0
    score = 0.6 * job_o + 0.25 * pain_o
    stars = hit.get("stars")
    if stars is not None:
        fame = "ghost" if stars <= 25 else ("niche" if stars <= 1500 else "known")
    else:
        url = (hit.get("url") or "").lower()
        fame = "catalog" if any(x in url for x in ("producthunt", "g2.com", "capterra", "alternativeto")) else "niche"
        if any(x in url for x in ("wikipedia", "forbes", "techcrunch", "medium.com")):
            fame = "known"
    # demote listicles
    title = (hit.get("title") or "").lower()
    if any(x in title for x in ("best ", "top 10", "top 15", "alternatives 20", "roundup")):
        score -= 0.2
        fame = "listicle"
    if hit.get("kind") == "repo" or (hit.get("lane") or "").startswith("oss"):
        score += 0.15
    hit = dict(hit)
    hit["fit_score"] = round(max(0.0, score), 3)
    hit["fame"] = fame
    if score >= 0.35:
        hit["fit"] = "strong"
    elif score >= 0.18:
        hit["fit"] = "partial"
    elif score >= 0.08:
        hit["fit"] = "adjacent"
    else:
        hit["fit"] = "noise"
    return hit


def multi_lane_hits(slots: HuntSlots, max_queries: int = 10) -> list[dict[str, Any]]:
    qs = seed_queries_for_problem(slots.problem, slots.job, slots.pain, slots.platform)
    for p in slots.products():
        qs.append(f"alternative to {p}")
        qs.append(f"switched from {p}")
        qs.append(f"{p} open source")
    if slots.platform:
        qs.append(f"{slots.job or slots.problem} {slots.platform}")
    hits: list[dict[str, Any]] = []
    seen: set[str] = set()
    for q in qs[:max_queries]:
        for h in tavily_search(q, max_results=5) + github_search_repos(q, limit=5):
            key = (h.get("url") or h.get("title") or "").rstrip("/").lower()
            if not key or key in seen:
                continue
            seen.add(key)
            hits.append(h)
        time.sleep(0.1)
    # ghost GH pass
    for q in (slots.job or slots.problem, *slots.products()[:2]):
        if not q:
            continue
        for h in github_search_repos(f"{q} stars:0..30", limit=6):
            key = (h.get("url") or "").rstrip("/").lower()
            if key and key not in seen:
                seen.add(key)
                hits.append(h)
    return hits


def run_hunt(
    slots: HuntSlots,
    *,
    max_queries: int = 12,
    max_tools: int = 40,
    max_closure_queries: int = 40,
    early_stage: bool = True,
    with_closure: bool = True,
) -> dict[str, Any]:
    """Full discovery: multi-lane hits + optional competitive closure on extracted tools."""
    hits = multi_lane_hits(slots, max_queries=max_queries)
    scored = [_score_hit(h, slots) for h in hits]
    scored = [h for h in scored if h.get("fit") != "noise"]
    scored.sort(key=lambda h: (-h["fit_score"], h.get("stars") if h.get("stars") is not None else 10**6))

    domain = slots.job or "software tools"
    closure_block: dict[str, Any] | None = None
    if with_closure:
        seeds = seed_queries_for_problem(slots.problem, slots.job, slots.pain, slots.platform)
        cr = competitive_closure(
            seeds,
            domain_phrase=domain[:40],
            max_tools=max_tools,
            max_queries=max_closure_queries,
            early_stage=early_stage,
        )
        closure_block = {
            "tools": cr.tools,
            "overflow": cr.overflow[:30],
            "closure_log": cr.closure_log,
            "stop_reason": cr.stop_reason,
            "queries_run": cr.queries_run,
            "closed": cr.closed,
        }

    checklist = []
    if slots.job:
        checklist.append(f"Primary job: {slots.job}")
    if slots.pain:
        checklist.append(f"Addresses pain: {slots.pain}")
    if slots.platform:
        checklist.append(f"Runs on: {slots.platform}")
    if slots.constraints:
        checklist.append(f"Respects: {slots.constraints}")
    if not checklist:
        checklist.append(f"Solves: {slots.problem}")

    return {
        "slots": asdict(slots),
        "checklist": checklist,
        "hits": scored[:40],
        "buckets": {
            "strong": [h for h in scored if h["fit"] == "strong"][:15],
            "partial": [h for h in scored if h["fit"] == "partial"][:15],
            "ghost": [h for h in scored if h.get("fame") in ("ghost", "niche")][:15],
        },
        "closure": closure_block,
        "disclaimer": "Does not certify absence. Only searched available web/GitHub sources.",
    }


def render_markdown(report: dict[str, Any]) -> str:
    slots = report["slots"]
    lines = [
        "# someone_already_made_it",
        "",
        f"**Problem:** {slots.get('problem')}",
        f"**Job:** {slots.get('job') or '—'}",
        f"**Pain:** {slots.get('pain') or '—'}",
        f"**Platform:** {slots.get('platform') or '—'}",
        f"**Constraints:** {slots.get('constraints') or '—'}",
        f"**Tried:** {slots.get('tried') or '—'}",
        "",
        "## Checklist",
    ]
    for c in report.get("checklist") or []:
        lines.append(f"- {c}")

    for label, key in [
        ("Strong matches", "strong"),
        ("Partial", "partial"),
        ("Ghost / niche", "ghost"),
    ]:
        lines.append(f"\n## {label}")
        rows = (report.get("buckets") or {}).get(key) or []
        if not rows:
            lines.append("_none_")
            continue
        for h in rows:
            stars = f" ★{h['stars']}" if h.get("stars") is not None else ""
            lines.append(
                f"- **[{h.get('title') or h.get('url')}]({h.get('url')})** "
                f"`{h.get('fame')}` score={h.get('fit_score')}{stars}\n"
                f"  {(h.get('content') or '')[:160]}"
            )

    cl = report.get("closure")
    if cl:
        lines.append("\n## Competitive closure (tool names)")
        lines.append(
            f"Stop: **{cl.get('stop_reason')}** · queries={cl.get('queries_run')} · "
            f"closed={cl.get('closed')}"
        )
        for t in (cl.get("tools") or [])[:30]:
            url = (t.get("urls") or [""])[0]
            if url:
                lines.append(f"- **{t['name']}** — {url} (evidence×{t.get('evidence_count', 0)})")
            else:
                lines.append(f"- **{t['name']}** (evidence×{t.get('evidence_count', 0)})")
        if cl.get("overflow"):
            lines.append("\nOverflow (past cap): " + ", ".join(cl["overflow"][:20]))

    lines.append(f"\n## Residual\n{report.get('disclaimer')}")
    return "\n".join(lines) + "\n"
