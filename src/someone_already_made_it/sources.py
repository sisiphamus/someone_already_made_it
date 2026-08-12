from __future__ import annotations

import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from typing import Any

from .env import tavily_key


def tavily_search(query: str, max_results: int = 6) -> list[dict[str, Any]]:
    key = tavily_key()
    if not key:
        return []
    body = json.dumps(
        {
            "api_key": key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return []
    out: list[dict[str, Any]] = []
    for r in data.get("results") or []:
        out.append(
            {
                "title": r.get("title") or "",
                "url": r.get("url") or "",
                "content": (r.get("content") or "")[:600],
                "lane": "web",
                "query": query,
            }
        )
    return out


def github_search_repos(query: str, limit: int = 6) -> list[dict[str, Any]]:
    q = re.sub(r"site:github\.com\s*", "", query, flags=re.I).strip()
    q = re.sub(r"[\"']", "", q)
    words = q.split()[:8]
    q = " ".join(words).strip()
    if len(q) < 3:
        return []
    results: list[dict[str, Any]] = []
    for variant in (q, f"{q} stars:0..50"):
        try:
            proc = subprocess.run(
                [
                    "gh",
                    "search",
                    "repos",
                    variant,
                    "--limit",
                    str(limit),
                    "--json",
                    "fullName,description,url,stargazersCount,updatedAt,isArchived,homepage",
                ],
                capture_output=True,
                text=True,
                timeout=45,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return results
        if proc.returncode != 0:
            continue
        try:
            rows = json.loads(proc.stdout or "[]")
        except json.JSONDecodeError:
            continue
        for row in rows:
            stars = row.get("stargazersCount") or 0
            results.append(
                {
                    "title": row.get("fullName") or "",
                    "url": row.get("url") or "",
                    "content": row.get("description") or "",
                    "stars": stars,
                    "updated": row.get("updatedAt"),
                    "archived": row.get("isArchived"),
                    "homepage": row.get("homepage") or "",
                    "lane": "oss-ghost" if stars <= 25 else "oss",
                    "query": variant,
                    "kind": "repo",
                }
            )
        time.sleep(0.25)
    return results


def has_web() -> bool:
    return bool(tavily_key())


def has_github() -> bool:
    try:
        proc = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
