from __future__ import annotations

import os
from pathlib import Path


def load_env() -> None:
    """Load KEY=VALUE from common env files without overriding existing env."""
    candidates = [
        Path.cwd() / ".env",
        Path.home() / ".env",
        Path("/home/adam/system/us/.env"),
    ]
    for path in candidates:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def tavily_key() -> str | None:
    return os.environ.get("TAVILY_API_KEY") or os.environ.get("TAVILY_KEY")
