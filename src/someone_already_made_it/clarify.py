from __future__ import annotations

import re
from typing import Any

KNOWN_PRODUCTS = [
    "Notion",
    "Obsidian",
    "Evernote",
    "Roam",
    "Logseq",
    "Fitbit",
    "Garmin",
    "Gmail",
    "Outlook",
    "Superhuman",
    "Slack",
    "Todoist",
    "Asana",
    "Trello",
    "Jira",
    "Linear",
    "Apple Notes",
    "OneNote",
    "Craft",
    "Coda",
    "Airtable",
    "Excel",
    "Google Docs",
    "Spotify",
    "Chrome",
]


def extract_mentioned_products(problem: str) -> list[str]:
    return [k for k in KNOWN_PRODUCTS if re.search(rf"\b{re.escape(k)}\b", problem, re.I)]


def plan_clarify(problem: str) -> dict[str, Any]:
    products = extract_mentioned_products(problem)
    slots: dict[str, Any] = {
        "product_mentioned": products[0] if products else None,
        "products": products,
        "raw": problem,
    }
    questions: list[dict[str, str]] = []

    dislike = bool(
        re.search(
            r"\b(don'?t like|hate|clunky|slow|broken|sucks|replace|tired of|leave|leaving|better than)\b",
            problem,
            re.I,
        )
    )
    if dislike:
        questions.append(
            {
                "id": "pain",
                "slot": "pain",
                "question": "What specifically bothers you about it? (speed, structure, offline, price, collab, AI, mobile, lock-in…)",
            }
        )
    elif products:
        questions.append(
            {
                "id": "gap",
                "slot": "pain",
                "question": "What can you not do today that you need? Be concrete.",
            }
        )

    questions.extend(
        [
            {
                "id": "job",
                "slot": "job",
                "question": "What are you actually trying to get done? (one sentence)",
            },
            {
                "id": "platform",
                "slot": "platform",
                "question": "Where must it run? (phone / laptop OS / browser / terminal / self-host)",
            },
            {
                "id": "constraints",
                "slot": "constraints",
                "question": "Hard constraints: budget, privacy, open-source, integrations?",
            },
            {
                "id": "tried",
                "slot": "tried",
                "question": "What have you already tried or ruled out?",
            },
        ]
    )
    # de-dupe by slot, max 5
    seen: set[str] = set()
    out_q = []
    for q in questions:
        if q["slot"] in seen:
            continue
        seen.add(q["slot"])
        out_q.append(q)
        if len(out_q) >= 5:
            break
    return {"problem": problem, "inferred_products": products, "questions": out_q}
