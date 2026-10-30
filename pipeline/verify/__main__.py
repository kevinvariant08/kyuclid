"""python -m pipeline.verify draft.json [--report out/report.json]
python -m pipeline.verify --batch dir/ [--concurrency 4]

Exit code: 0 if every draft passes, 1 if any fails or needs investigating, 3 if a model call errored.
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import gate
from .backend import ModelError, make_backend
from .config import OUT


def summarise(reports):
    """The cost summary for a batch: the plan-usage estimate per draft that reached a model, and overall."""
    models = {}
    for r in reports:
        for m, u in r["usage"]["by_model"].items():
            t = models.setdefault(m, dict(calls=0, output=0, thinking=0, usd=0.0))
            t["calls"] += u["calls"]
            t["output"] += u["output"]
            t["thinking"] += u["thinking"]
            t["usd"] = round(t["usd"] + u["usd"], 4)
    used = [r for r in reports if r["usage"]["calls"]]
    total = sum(r["usage"]["api_equivalent_usd"] for r in reports)
    return dict(
        drafts=len(reports),
        verdicts={k: sum(r["verdict"].split(" ")[0] == k for r in reports) for k in ("PASS", "FAIL", "INVESTIGATE", "ERROR")},
        drafts_reaching_a_model=len(used),
        model_calls=sum(r["usage"]["calls"] for r in reports),
        by_model=models,
        api_equivalent_usd_total=round(total, 4),
        api_equivalent_usd_this_run=round(sum(r["usage"]["api_equivalent_usd_this_run"] for r in reports), 4),
        api_equivalent_usd_per_model_draft=round(total / len(used), 4) if used else 0,
        output_tokens_per_model_draft=round(sum(r["usage"]["output_tokens"] for r in reports) / len(used)) if used else 0,
        note="On the CLI backend this is an estimate of plan usage at API list prices, not money spent.",
    )


def run_batch(paths, backend, out_dir, concurrency, **kw):
    """Runs drafts in parallel. If the plan limit is hit, drafts not yet started are left out; re-running resumes from the cache."""
    stopped = []

    def one(path):
        if stopped:
            return None
        draft = json.loads(Path(path).read_text(encoding="utf-8"))
        report = gate.verify(draft, backend, **kw)
        gate.write_report(report, out_dir / f"{Path(path).stem}.json")
        print(f"{report['id']}: {report['verdict']}", flush=True)
        if report["plan_limit"]:
            stopped.append(report["id"])
        return report

    with ThreadPoolExecutor(concurrency) as pool:
        reports = [r for r in pool.map(one, paths) if r]
    summary = summarise(reports)
    summary["stopped_at_plan_limit"] = bool(stopped)
    summary["not_run"] = len(paths) - len(reports)
    gate.write_report(summary, out_dir / "_summary.json")
    return reports, summary


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="python -m pipeline.verify")
    ap.add_argument("draft", nargs="?")
    ap.add_argument("--batch", help="a folder of draft JSON files")
    ap.add_argument("--report", help="report path (default out/report.json, or out/batch/ with --batch)")
    ap.add_argument("--backend", choices=["cli", "api"], default="cli", help="cli uses the plan; api needs ANTHROPIC_API_KEY and costs money")
    ap.add_argument("--concurrency", type=int, default=4, help="the limit on model calls at once, and on drafts at once in a batch")
    ap.add_argument("--keep-going", action="store_true", help="run every check even after a failure")
    ap.add_argument("--no-cache", action="store_true", help="repeat model calls even if a cached reply exists")
    args = ap.parse_args()
    if bool(args.draft) == bool(args.batch):
        ap.error("give one draft or --batch dir/")
    try:
        backend = make_backend(args.backend, args.concurrency)
    except ModelError as e:
        print(f"ERROR backend: {e}", file=sys.stderr)
        return 3
    backend.use_cache = not args.no_cache

    if args.batch:
        paths = sorted(p for p in Path(args.batch).glob("*.json") if not p.name.startswith("_"))
        out_dir = Path(args.report) if args.report else OUT / "batch"
        reports, summary = run_batch(paths, backend, out_dir, args.concurrency, keep_going=args.keep_going)
        print(json.dumps(summary, indent=2))
        verdicts = [r["verdict"] for r in reports]
    else:
        report = gate.verify(json.loads(Path(args.draft).read_text(encoding="utf-8")), backend, keep_going=args.keep_going)
        gate.write_report(report, Path(args.report) if args.report else OUT / "report.json")
        print(report["verdict"])
        verdicts = [report["verdict"]]
    if any(v.startswith("ERROR") for v in verdicts):
        return 3
    return 0 if all(v == "PASS" for v in verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
