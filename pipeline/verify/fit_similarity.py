"""Fits the automatic-fail threshold from 20 deliberate reskins and 20 different problems on the same technique.

    python -m pipeline.verify.fit_similarity            free: writes similarity.json
    python -m pipeline.verify.fit_similarity --judge    also tests the judge on all 40 pairs (40 model calls)

An automatic fail skips the judge, so it must not catch honest problems. The threshold therefore sits just
above the most similar same-technique pair, whatever that does to recall. The judge handles the rest.
Word weights depend on what is indexed, so fit with the corpus configured: similarities computed against the
bank alone aren't comparable. The threshold also stays above the 97th percentile of what real corpus problems
reach against each other, because 11% of them pass 0.5 (short statements share most of their words).
Only numbers are stored.
"""
import argparse
import json
import random
from concurrent.futures import ThreadPoolExecutor

from . import originality, prompts
from .backend import Usage, last_json, make_backend
from .config import HERE, ROLES, corpus_path

PAIRS = HERE / "tests" / "originality_pairs.json"


def _corpus_ceiling(records, n=800, quantile=0.97):
    """The similarity honest corpus problems reach against each other. Above it are mostly real repeats and bare arithmetic."""
    corpus = [r for r in records if r["source"] == "corpus"]
    if not corpus:
        return None
    index = originality.Index(corpus)
    tops = []
    for r in random.Random(5).sample(corpus, min(n, len(corpus))):
        s = index.similarities(r["text"], exclude={r["id"]})
        tops.append(s[0][1] if s else 0.0)
    tops.sort()
    return round(tops[int(quantile * len(tops))], 2)


def fit():
    data = json.loads(PAIRS.read_text(encoding="utf-8"))
    pairs = [(p, True) for p in data["reskins"]] + [(p, False) for p in data["same_technique"]]
    path = corpus_path()
    base = originality.load_bank() + (originality.load_corpus(path) if path and path.is_dir() else [])
    records = base + [dict(id=f"pair-{i}", text=p["a"], source="bank") for i, (p, _) in enumerate(pairs)]
    index = originality.Index(records)
    sims = []
    for i, (p, is_reskin) in enumerate(pairs):
        s = dict((r["id"], v) for r, v in index.similarities(p["b"])).get(f"pair-{i}", 0.0)
        sims.append((s, is_reskin))
    neg, pos = [s for s, r in sims if not r], [s for s, r in sims if r]
    ceiling = _corpus_ceiling(base)
    threshold = round(max(max(neg) + 0.05, ceiling or 0.5), 2)
    caught = sum(s >= threshold for s in pos)
    result = dict(auto_fail=threshold, fitted_on="tests/originality_pairs.json: 20 reskins, 20 same-technique pairs",
                  same_technique_max=round(max(neg), 3), same_technique_mean=round(sum(neg) / len(neg), 3),
                  reskin_mean=round(sum(pos) / len(pos), 3), reskin_max=round(max(pos), 3), reskins_auto_caught=caught,
                  indexed_records=len(base), corpus_p97_top_similarity=ceiling,
                  note="TF-IDF only catches reskins that keep the wording. The judge catches the rest; see README.")
    (HERE / "similarity.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    return data


def test_judge(data, concurrency=4):
    """Asks only about the pair, with the 'known' question ignored, because that is what the threshold fit is about."""
    backend = make_backend("cli", concurrency)
    usage = Usage()
    model, effort, cap = ROLES["originality"]

    def one(item):
        i, p, expected = item
        draft = dict(statement=p["b"])
        nbr = [dict(id="n", text=p["a"])]
        r = backend.call(model, prompts.ORIGINALITY, prompts.originality(draft, nbr), effort, cap, salt=f"pair-{i}", role="originality", draft_id=f"pair-{i}")
        usage.add(r)
        d = last_json(r.text) or {}
        said = any(v.get("reskin") for v in d.get("neighbours", []))
        return dict(pair=i, expected=expected, said=said, reason=str((d.get("neighbours") or [{}])[0].get("reason", ""))[:120])

    items = [(i, p, True) for i, p in enumerate(data["reskins"])] + [(100 + i, p, False) for i, p in enumerate(data["same_technique"])]
    with ThreadPoolExecutor(concurrency) as pool:
        rows = list(pool.map(one, items))
    tp = sum(r["said"] and r["expected"] for r in rows)
    fp = sum(r["said"] and not r["expected"] for r in rows)
    out = dict(reskins_caught=f"{tp}/20", false_alarms=f"{fp}/20", usage=usage.summary(), misses=[r for r in rows if r["said"] != r["expected"]])
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true")
    args = ap.parse_args()
    pairs = fit()
    if args.judge:
        test_judge(pairs)
