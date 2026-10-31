"""Check 7: is the draft a copy or a reskin of something published?

There's no embeddings endpoint on the plan, so "embedding" here is local TF-IDF over the statement, with
numbers and single-letter variables masked so that changing them doesn't help. That catches near copies.
A reskin in a new setting has few words in common with its source, so the judge is what catches those.

Corpus text may reach the judge's prompt but must never reach a report, a cache or this repo. Reports
hold IDs and scores only, and judge reasons pass through redact().
"""
import json
import math
import re
from collections import Counter
from pathlib import Path

from . import answers, prompts
from .backend import last_json
from .config import BANK_DIR, HERE, ROLES, corpus_path

SIMILARITY = HERE / "similarity.json"
STOP = set("a an and are as at be by can each find for from given has have how if in is it its let many of on or such that the then there this to two was we what which with".split())
N_NEIGHBOURS = 5
CONTEST_SOURCE = r"\b(AIME|AMC|USAMO|USAJMO|UKMT|BMO|IMO|ISL|EGMO|CGMO|APMO|RMM|HMMT|ARML|PUMaC|CMIMC|SMT|Olympiad)\b"


def mask(text):
    t = re.sub(r"\\[a-zA-Z]+", lambda m: " " + m.group()[1:] + " ", text.lower())
    return re.sub(r"\s+", " ", re.sub(r"\d+(\.\d+)?", " num ", re.sub(r"[^a-z0-9. ]", " ", t))).strip()


def _word_features(masked):
    words = [w for w in re.findall(r"[a-z]+", masked) if len(w) > 1 and w not in STOP]
    return Counter(words + [a + "_" + b for a, b in zip(words, words[1:])])


def _char_features(masked):
    s = re.sub(r"[^a-z ]", "", masked)
    return Counter(s[i:i + n] for n in (3, 4, 5) for i in range(len(s) - n + 1))


class Tfidf:
    """A cosine index over one kind of feature. Query vectors use the same IDF."""

    def __init__(self, docs):
        self.df = Counter(f for d in docs for f in d)
        self.n = max(len(docs), 1)
        self.post = {}
        for i, d in enumerate(docs):
            for f, w in self.vector(d).items():
                self.post.setdefault(f, []).append((i, w))

    def vector(self, counts):
        v = {f: (1 + math.log(c)) * math.log(1 + self.n / (1 + self.df.get(f, 0))) for f, c in counts.items()}
        norm = math.sqrt(sum(w * w for w in v.values())) or 1
        return {f: w / norm for f, w in v.items()}

    def query(self, counts):
        scores = Counter()
        for f, w in self.vector(counts).items():
            for i, dw in self.post.get(f, ()):
                scores[i] += w * dw
        return scores


class Index:
    """Everything a draft is compared with: each corpus record and each problem in the bank."""

    def __init__(self, records):
        self.records = records
        masked = [mask(r["text"]) for r in records]
        self.words = Tfidf([_word_features(m) for m in masked])
        self.chars = Tfidf([_char_features(m) for m in masked])
        ideas = [(i, mask(r["core_idea"])) for i, r in enumerate(records) if r.get("core_idea")]
        self.idea_ids = [i for i, _ in ideas]
        self.ideas = Tfidf([_word_features(m) for _, m in ideas]) if ideas else None

    def similarities(self, text, core_idea=None, exclude=()):
        m = mask(text)
        w, c = self.words.query(_word_features(m)), self.chars.query(_char_features(m))
        s = Counter()
        for i in set(w) | set(c):
            s[i] = 0.5 * w[i] + 0.5 * c[i]
        if core_idea and self.ideas:
            for j, v in self.ideas.query(_word_features(mask(core_idea))).items():
                i = self.idea_ids[j]
                s[i] = max(s[i], v)
        return [(self.records[i], v) for i, v in s.most_common() if self.records[i]["id"] not in exclude]


def load_corpus(path):
    """Reads corpus/*.jsonl and joins <exam>_analysis.jsonl by id for core_idea, once task 03 writes it."""
    records, ideas = [], {}
    for f in sorted(Path(path).glob("*.jsonl")):
        rows = [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
        if f.stem.endswith("_analysis"):
            ideas.update({r["id"]: r.get("core_idea") for r in rows})
        else:
            records += [dict(id=r["id"], text=r.get("statement_md") or "", source="corpus", answer=r.get("answer_value")) for r in rows if r.get("statement_md")]
    for r in records:
        r["core_idea"] = ideas.get(r["id"])
    return records


def load_bank(bank_dir=BANK_DIR):
    return [dict(id=p["id"], text=p["statement"], source="bank") for p in (json.loads(f.read_text(encoding="utf-8")) for f in sorted(Path(bank_dir).glob("*.json")))]


_cached = {}


def default_index():
    """Built once per process, so a batch shares it. It is never written to disk."""
    path = corpus_path()
    key = str(path)
    if key not in _cached:
        records = load_bank() + (load_corpus(path) if path and path.is_dir() else [])
        _cached[key] = Index(records)
    return _cached[key], bool(path and path.is_dir())


def load_threshold():
    return json.loads(SIMILARITY.read_text(encoding="utf-8"))["auto_fail"]


def redact(reason, neighbours):
    """Drops a judge's reason if it shares 8 or more consecutive words with a neighbour, in case it quoted one."""
    words = re.findall(r"\w+", str(reason).lower())
    grams = {tuple(words[i:i + 8]) for i in range(len(words) - 7)}
    for n in neighbours:
        w = re.findall(r"\w+", n["text"].lower())
        if grams & {tuple(w[i:i + 8]) for i in range(len(w) - 7)}:
            return "[reason removed: it quoted a neighbour]"
    return str(reason)


def classical_rule(draft):
    """Rule 1: a classical problem outside the book can't quote a contest. Theorems wait for Kevin's decision."""
    prov = draft.get("provenance", {})
    if prov.get("kind") != "classical":
        return None
    if prov.get("book"):
        return "pass", f"classical, from {prov['book']}, which rule 1 allows", {}
    src = prov.get("source", "")
    if re.search(CONTEST_SOURCE, src):
        return "fail", f"quotes a contest problem ({src}) and isn't from the book, which rule 1 forbids", {"source": src}
    return "investigate", f"classical ({src}), not original: whether it can appear with attribution is Kevin's decision", {"source": src}


def lexical(draft, index, threshold):
    """Free and quick, so the gate runs it before spending anything on models."""
    sims = index.similarities(draft["statement"], draft.get("core_idea"), exclude={draft["id"]})
    top = sims[:N_NEIGHBOURS]
    ev = dict(nearest=[dict(id=r["id"], source=r["source"], similarity=round(v, 3)) for r, v in top], threshold=threshold)
    if top and top[0][1] >= threshold:
        return "fail", f"near-duplicate of {top[0][0]['id']}: similarity {top[0][1]:.2f} is over the {threshold:.2f} limit", ev
    return "pass", f"nearest {top[0][0]['id']} at {top[0][1]:.2f}" if top else "nothing to compare with", ev


def neighbours_for(draft, index):
    sims = index.similarities(draft["statement"], draft.get("core_idea"), exclude={draft["id"]})
    chosen = [r for r, _ in sims[:N_NEIGHBOURS]]
    # The inspiration is always examined, even if it isn't among the nearest.
    source = draft.get("inspired_by")
    if source and source not in {r["id"] for r in chosen}:
        extra = [r for r in index.records if r["id"] == source]
        chosen = chosen[:N_NEIGHBOURS - len(extra)] + extra
    return chosen


def ensure_core_idea(draft, index, backend, usage):
    """A cheap Haiku abstraction, used only if there are corpus core_ideas to compare it with."""
    if draft.get("core_idea") or not index.ideas:
        return draft
    model, effort, cap = ROLES["abstract"]
    r = backend.call(model, prompts.ABSTRACT, draft["statement"], effort, cap, role="abstract", draft_id=draft["id"])
    usage.add(r)
    return {**draft, "core_idea": r.text.strip()}


def judge(draft, index, backend, usage, has_corpus):
    draft = ensure_core_idea(draft, index, backend, usage)
    nbrs = neighbours_for(draft, index)
    model, effort, cap = ROLES["originality"]
    has_corpus_text = any(n["source"] == "corpus" for n in nbrs)
    r = backend.call(model, prompts.ORIGINALITY, prompts.originality(draft, nbrs), effort, cap, cacheable=not has_corpus_text, role="originality", draft_id=draft["id"])
    usage.add(r)
    d = last_json(r.text)
    if d is None:
        # The raw reply isn't quoted here, because it may contain corpus text.
        return "fail", "originality judge reply unreadable", {"model": r.model}
    verdicts = [dict(id=str(v.get("id")), reskin=bool(v.get("reskin")), reason=redact(v.get("reason", ""), nbrs)) for v in d.get("neighbours", [])]
    known = d.get("known") or {}
    ev = dict(model=r.model, corpus_available=has_corpus, neighbours_examined=[n["id"] for n in nbrs], verdicts=verdicts,
              known=dict(is_known=bool(known.get("is_known")), name=redact(known.get("name", ""), nbrs), reason=redact(known.get("reason", ""), nbrs)))
    if draft.get("core_idea"):
        ev["core_idea_used"] = True
    for v in verdicts:
        if v["reskin"]:
            return "fail", f"reskin of {v['id']}: {v['reason']}", ev
    if ev["known"]["is_known"]:
        return "fail", f"known problem: {ev['known']['name']}: {ev['known']['reason']}", ev
    return "pass", f"not a reskin of the {len(nbrs)} nearest" + ("" if has_corpus else " (bank only: no corpus available)") + ", and not a known problem", ev
