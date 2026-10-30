"""Runs the seed problems through the gate and writes SEED_VERDICTS.md. The gate's reasons hold IDs, never corpus text.

    python -m pipeline.verify.run_seeds [--check-only]

--check-only runs just the free checks: each seed's key against its hash, and its program in the sandbox.
"""
import argparse
import json
import re
import sys

from . import answers, computational, gate
from .__main__ import run_batch, summarise
from .backend import make_backend
from .config import BANK_DIR, HERE, OUT
from .seeds.programs import SEEDS


def seed_drafts():
    out = []
    for f in sorted(BANK_DIR.glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        if p["type"] == "answer":
            p["answer"], program = SEEDS[p["id"]]
            p["check_program"] = program.strip() + "\n"
        out.append(p)
    return out


def check_only(drafts):
    bad = 0
    for d in drafts:
        if d["type"] != "answer":
            continue
        hash_ok = answers.answer_hash(d["id"], d["answer"]) == d["answer_hash"]
        status, reason, _ = computational.run_program_check(d)
        print(f"{d['id']}: hash {'ok' if hash_ok else 'WRONG'}, program {status}: {reason}")
        bad += (not hash_ok) + (status != "pass")
    return bad


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()
    drafts = seed_drafts()
    if args.check_only:
        return 1 if check_only(drafts) else 0
    tmp = OUT / "seed_drafts"
    tmp.mkdir(parents=True, exist_ok=True)
    paths = []
    for d in drafts:
        path = tmp / f"{d['id']}.json"
        path.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
        paths.append(path)
    reports, summary = run_batch(paths, make_backend("cli", args.concurrency), OUT / "seeds", args.concurrency, keep_going=True)
    write_table(reports, summary)
    print(json.dumps(summary, indent=2))
    return 0


def public(reason):
    """This file is public, and a judge's reason beside a seed can come close to describing the corpus problem. Keep only the ID or the name."""
    reason = re.sub(r"(reskin of [\w-]+):.*", r"\1", reason)
    return re.sub(r"(known problem: [^:]+):.*", r"\1", reason)


def write_table(reports, summary):
    lines = ["# Seed problem verdicts", "",
             "From `python -m pipeline.verify.run_seeds`, which runs every check even after a failure. The verdict names the first failure in the brief's order; the last column lists any others. Judges' full reasons are in the private reports under `out/seeds/`.",
             "", "| Problem | Verdict | Blind solves | Estimated kyu | Other failures |", "|---|---|---|---|---|"]
    for r in sorted(reports, key=lambda r: r["id"]):
        checks = {c["check"]: c for c in r["checks"]}
        b = checks.get("blind_solves", {}).get("evidence", {})
        solved = f"{b['right']}/{b['total']}" if "right" in b else "n/a"
        est = checks.get("difficulty", {}).get("evidence", {}).get("estimated_kyu", "n/a")
        fails = [c for c in r["checks"] if c["status"] in ("fail", "investigate")]
        rest = "; ".join(f"{c['check']}: {public(c['reason'])}" for c in fails if not r["verdict"].split(":")[0].endswith(c["check"].replace("_lexical", "")))
        lines.append(f"| {r['id']} | {public(r['verdict']).replace('|', '/')} | {solved} | {est} | {rest.replace('|', '/')} |")
    lines += ["", "## Usage", "", f"{summary['model_calls']} model calls across {summary['drafts_reaching_a_model']} problems, {summary['output_tokens_per_model_draft']} output tokens a problem, about ${summary['api_equivalent_usd_per_model_draft']} a problem at API list prices. On the plan this is usage, not money.", ""]
    (HERE / "SEED_VERDICTS.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    sys.exit(main())
