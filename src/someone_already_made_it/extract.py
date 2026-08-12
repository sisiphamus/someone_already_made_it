from __future__ import annotations

import re
from typing import Any

# Titles / descriptions that look like products or repos
_SKIP = re.compile(
    r"^(best|top|how to|what is|vs\.?|alternatives?|compare|guide|blog)\b",
    re.I,
)
_NAME = re.compile(
    r"\b([A-Z][A-Za-z0-9]{1,}(?:[ .-][A-Z][A-Za-z0-9]+){0,3})\b"
)
_REPO = re.compile(r"github\.com/([\w.-]+)/([\w.-]+)", re.I)

# Common non-product words
_STOP = {
    "The",
    "This",
    "That",
    "With",
    "From",
    "Using",
    "About",
    "After",
    "Before",
    "When",
    "Where",
    "What",
    "How",
    "Why",
    "Your",
    "Our",
    "New",
    "Free",
    "Open",
    "Source",
    "Google",
    "Microsoft",
    "Amazon",
    "Apple",
    "GitHub",
    "Reddit",
    "Medium",
    "YouTube",
    "Wikipedia",
    "API",
    "SDK",
    "LLM",
    "AI",
    "RAG",
}


def names_from_hit(hit: dict[str, Any]) -> list[str]:
    found: list[str] = []
    url = hit.get("url") or ""
    m = _REPO.search(url)
    if m:
        found.append(f"{m.group(1)}/{m.group(2)}")
        # also short product-ish repo name
        repo = m.group(2).replace("-", " ").replace("_", " ")
        if len(repo) > 2:
            found.append(repo.title() if " " in repo else m.group(2))

    title = (hit.get("title") or "").strip()
    # strip " - GitHub" etc
    title = re.split(r"\s+[|\-–—]\s+", title)[0].strip()
    if title and not _SKIP.match(title) and len(title) < 60:
        # single brand token
        first = title.split()[0] if title.split() else ""
        if first and first not in _STOP and len(first) > 1:
            found.append(first)
        if " " not in title and title not in _STOP:
            found.append(title)

    content = hit.get("content") or ""
    for m in _NAME.finditer(content[:400]):
        name = m.group(1)
        if name in _STOP or len(name) < 3:
            continue
        if name.lower() in {"http", "https", "www"}:
            continue
        found.append(name)

    # normalize
    out: list[str] = []
    seen: set[str] = set()
    for n in found:
        n = n.strip().rstrip(".,;:")
        key = n.lower()
        if key in seen or len(n) < 2:
            continue
        seen.add(key)
        out.append(n)
    return out[:8]
