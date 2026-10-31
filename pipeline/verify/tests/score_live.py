"""Compares a live --batch run with tests/expected.json.

    python -m pipeline.verify --batch pipeline/verify/tests/drafts --report out/suite
    python -m pipeline.verify.tests.score_live out/suite
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "out/suite")
    expected = json.loads((HERE / "expected.json").read_text(encoding="utf-8"))
    bad = missing = 0
    for pid, e in sorted(expected.items()):
        path = out / f"{pid}.json"
        if not path.exists():
            missing += 1
            print(f"MISSING {pid}")
            continue
        verdict = json.loads(path.read_text(encoding="utf-8"))["verdict"]
        m = re.match(r"\w+ (\w+):", verdict)
        allowed = {c.replace("originality_lexical", "originality") for c in e["checks"] or []}
        ok = verdict.split(" ")[0] in e["verdict"] and (not allowed or (m and m.group(1) in allowed))
        if not ok:
            bad += 1
            print(f"MISMATCH {pid}: wanted {e['verdict']} {sorted(allowed)}, got: {verdict}")
    print(f"{len(expected) - bad - missing}/{len(expected)} as expected, {bad} mismatched, {missing} missing")
    s = json.loads((out / "_summary.json").read_text(encoding="utf-8"))
    print(json.dumps({k: s[k] for k in ("verdicts", "drafts_reaching_a_model", "model_calls", "by_model", "api_equivalent_usd_total", "api_equivalent_usd_this_run", "api_equivalent_usd_per_model_draft", "output_tokens_per_model_draft", "stopped_at_plan_limit", "not_run")}, indent=1))
    return 1 if bad or missing else 0


if __name__ == "__main__":
    sys.exit(main())
