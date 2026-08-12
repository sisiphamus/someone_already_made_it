from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .clarify import plan_clarify
from .closure import competitive_closure, seed_queries_for_problem
from .env import load_env
from .hunt import HuntSlots, render_markdown, run_hunt
from .sources import has_github, has_web


def cmd_doctor(_: argparse.Namespace) -> int:
    load_env()
    print("someone_already_made_it doctor")
    print(f"  Tavily web search: {'OK' if has_web() else 'MISSING (set TAVILY_API_KEY)'}")
    print(f"  GitHub (gh auth):  {'OK' if has_github() else 'MISSING (install gh + gh auth login)'}")
    if not has_web() and not has_github():
        print("No search backends. At least one of Tavily or gh is required.", file=sys.stderr)
        return 1
    return 0


def cmd_clarify(args: argparse.Namespace) -> int:
    plan = plan_clarify(args.problem)
    print(json.dumps(plan, indent=2))
    print("\n--- Ask the user (in order) ---", file=sys.stderr)
    for i, q in enumerate(plan["questions"], 1):
        print(f"{i}. [{q['slot']}] {q['question']}", file=sys.stderr)
    return 0


def cmd_discover(args: argparse.Namespace) -> int:
    load_env()
    if not has_web() and not has_github():
        print("Need TAVILY_API_KEY and/or gh auth. Run: sami doctor", file=sys.stderr)
        return 1
    slots = HuntSlots(
        problem=args.problem,
        job=args.job or "",
        pain=args.pain or "",
        platform=args.platform or "",
        constraints=args.constraints or "",
        tried=args.tried or "",
    )
    report = run_hunt(
        slots,
        max_queries=args.max_queries,
        max_tools=args.max_tools,
        max_closure_queries=args.max_closure_queries,
        early_stage=not args.no_early_stage,
        with_closure=not args.no_closure,
    )
    if args.json:
        # sets not json serializable — already plain in report
        print(json.dumps(report, indent=2, default=str))
    else:
        print(render_markdown(report))
    if args.out:
        Path(args.out).write_text(
            json.dumps(report, indent=2, default=str) if args.json else render_markdown(report),
            encoding="utf-8",
        )
        print(f"Wrote {args.out}", file=sys.stderr)
    return 0


def cmd_category(args: argparse.Namespace) -> int:
    """List tools for a category with competitive closure only (no problem slots)."""
    load_env()
    if not has_web() and not has_github():
        print("Need TAVILY_API_KEY and/or gh auth. Run: sami doctor", file=sys.stderr)
        return 1
    seeds = [
        f"{args.category} tools",
        f"{args.category} software",
        f"{args.category} open source",
        f"best {args.category} for AI",
        f"{args.category} API",
    ]
    cr = competitive_closure(
        seeds,
        domain_phrase=args.domain or args.category,
        max_tools=args.max_tools,
        max_queries=args.max_queries,
        early_stage=not args.no_early_stage,
    )
    out = {
        "category": args.category,
        "tools": cr.tools,
        "overflow": cr.overflow,
        "closure_log": cr.closure_log,
        "stop_reason": cr.stop_reason,
        "queries_run": cr.queries_run,
        "closed": cr.closed,
    }
    if args.json:
        print(json.dumps(out, indent=2, default=str))
    else:
        print(f"# Category: {args.category}\n")
        print(f"Stop: {cr.stop_reason} · queries={cr.queries_run} · closed={cr.closed}\n")
        for t in cr.tools:
            url = (t.get("urls") or [""])[0]
            print(f"- **{t['name']}**" + (f" — {url}" if url else ""))
        if cr.overflow:
            print("\nOverflow:", ", ".join(cr.overflow[:25]))
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    load_env()
    plan = plan_clarify(args.problem)
    print(f"\nProblem: {args.problem}\n")
    if plan["inferred_products"]:
        print(f"(heard: {', '.join(plan['inferred_products'])})\n")
    answers: dict[str, str] = {}
    for i, q in enumerate(plan["questions"], 1):
        print(f"{i}/{len(plan['questions'])}  {q['question']}")
        try:
            ans = input("> ").strip()
        except EOFError:
            ans = ""
        if ans:
            answers[q["slot"]] = ans
        print()
    args.job = answers.get("job", "")
    args.pain = answers.get("pain", "")
    args.platform = answers.get("platform", "")
    args.constraints = answers.get("constraints", "")
    args.tried = answers.get("tried", "")
    args.json = False
    args.out = None
    return cmd_discover(args)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="someone-already-made-it",
        description="Find existing tools/products/repos/companies for a problem (competitive closure).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor", help="Check search backends")
    d.set_defaults(func=cmd_doctor)

    c = sub.add_parser("clarify", help="Emit refining questions as JSON")
    c.add_argument("problem")
    c.set_defaults(func=cmd_clarify)

    h = sub.add_parser("discover", help="Discover solutions for a problem")
    h.add_argument("problem")
    h.add_argument("--job", default="")
    h.add_argument("--pain", default="")
    h.add_argument("--platform", default="")
    h.add_argument("--constraints", default="")
    h.add_argument("--tried", default="")
    h.add_argument("--max-queries", type=int, default=10)
    h.add_argument("--max-tools", type=int, default=40)
    h.add_argument("--max-closure-queries", type=int, default=40)
    h.add_argument("--no-closure", action="store_true")
    h.add_argument("--no-early-stage", action="store_true")
    h.add_argument("--json", action="store_true")
    h.add_argument("--out", default=None)
    h.set_defaults(func=cmd_discover)

    cat = sub.add_parser("category", help="List tools in a category with competitive closure")
    cat.add_argument("category")
    cat.add_argument("--domain", default="")
    cat.add_argument("--max-tools", type=int, default=40)
    cat.add_argument("--max-queries", type=int, default=45)
    cat.add_argument("--no-early-stage", action="store_true")
    cat.add_argument("--json", action="store_true")
    cat.set_defaults(func=cmd_category)

    a = sub.add_parser("ask", help="Interactive clarify + discover")
    a.add_argument("problem")
    a.add_argument("--max-queries", type=int, default=10)
    a.add_argument("--max-tools", type=int, default=40)
    a.add_argument("--max-closure-queries", type=int, default=40)
    a.add_argument("--no-closure", action="store_true")
    a.add_argument("--no-early-stage", action="store_true")
    a.set_defaults(func=cmd_ask)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
