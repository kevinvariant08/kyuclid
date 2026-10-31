"""Turns a candidate into a gate draft, and runs the free checks that keep a bad one from costing anything."""
import json
import re
import threading

from ..verify import answers, originality, sandbox, schema_check, standard
from ..verify.config import BANK_DIR
from .config import AUTHOR, HELD, PENDING, TAXONOMY

_taken = set()
_lock = threading.Lock()


def slug(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:56].strip("-")
    return s or "untitled"


def allocate_id(title, owner):
    """IDs are permanent and public, so they come from the title. owner lets a repair keep its own ID."""
    base = slug(title)
    with _lock:
        n = 1
        while True:
            pid = base if n == 1 else f"{base}-{n}"
            taken = (pid, owner) not in _taken and any(p == pid for p, _ in _taken)
            on_disk = any((d / f"{pid}.json").exists() for d in (BANK_DIR, PENDING, HELD))
            if not taken and not on_disk:
                _taken.add((pid, owner))
                return pid
            n += 1


def build(idea, write, key, inp, kyu, profile, run):
    pid = allocate_id(idea["title"], inp.id)
    return dict(
        id=pid, title=idea["title"], kyu=kyu, topic=idea["topic"] if idea["topic"] in tuple("ACGN") else inp.record["topic"], subtopics=write["subtopics"],
        type=profile.type, status="draft", statement=idea["statement"], answer_format=profile.answer_format,
        answer_hash=answers.answer_hash(pid, key), hints=write["hints"], solution=write["solution"],
        provenance=dict(kind="original", author=AUTHOR, pipeline_run=run), stats=dict(solves=0, attempts=0, liked=0),
        answer=key, check_program=idea["check_program"], inspired_by=inp.id, variation_recipe=idea["recipe"],
    )


def taxonomy_ids():
    t = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    return {x["id"] for x in t["techniques"] + t["configurations"] if x.get("status") != "legacy"}


WHY = re.compile(r"^<b>Why this works\.</b> <code>[a-z0-9-]+</code>(, <code>[a-z0-9-]+</code>)*: .+$", re.S)


def _lint_text(text):
    if re.search(r"\*\*|`|^\s*[-*] ", text, re.M):
        return "Markdown isn't rendered: use <b> and <code>, and no lists (S10)"
    for tex, _ in schema_check.split_math(text)[0]:
        if "*" in tex or re.search(r"\\leq\b|\\geq\b|\\frac\d", tex):
            return f"LaTeX convention (S9): no *, \\leq, \\geq or \\frac12, found in ${tex[:40]}$"
    return None


def lint_idea(idea):
    """Rules on the statement and title that the standard makes automatic and the gate doesn't yet check."""
    problem = _lint_text(idea["statement"])
    if problem:
        return problem
    if re.search(r"\([a-c]\)\s", standard._prose(idea["statement"])) or idea["statement"].count("?") > 1:
        return "a statement asks exactly one thing (S1)"
    if re.search(standard.CONTESTS, idea["title"]) or slug(idea["title"]) in taxonomy_ids():
        return "the title gives away a contest or a technique (S12, S13)"
    return None


def lint_key(idea, key):
    """A1 and A6, on what the program printed."""
    try:
        value = int(key)
    except ValueError:
        return f"the key must be a plain integer from 2 to 999 (A1), but the program printed {key or 'nothing'}"
    if not 0 <= value <= 999:
        return f"the key must be from 2 to 999 (A1), but the program printed {value}: change the parameters or ask for a remainder modulo $1000$"
    if value in (0, 1):
        return f"a key of {value} is guessable (A6)"
    if re.search(rf"(?<![\d.]){value}(?![\d.])", re.sub(r"[\\{}^_]", " ", idea["statement"])):
        return f"the key {value} appears in the statement (A6)"
    return None


def lint(d):
    """Rules on the write-up. Returns the first problem, or None."""
    known = taxonomy_ids()
    bad = [s for s in d["subtopics"] if s not in known]
    if bad:
        return f"subtopics not in the taxonomy (M5): {', '.join(bad[:4])}"
    paras = [p.strip() for p in d["solution"].split("\n\n") if p.strip()]
    if not WHY.match(paras[-1]):
        return 'the last paragraph must be exactly the "Why this works" line (M4): <b>Why this works.</b> <code>id-one</code>, <code>id-two</code>: one clause'
    missing = [u for u in re.findall(r"<code>([a-z0-9-]+)</code>", paras[-1]) if u not in d["subtopics"]]
    if missing:
        return f"the Why this works line uses IDs not in subtopics (M4): {', '.join(missing)}"
    if not re.search(rf"(?<![\d.]){re.escape(d['answer'])}(?![\d.])", "\n\n".join(paras[-3:-1])):
        return "the solution must state the final answer just before the Why this works line (M3)"
    for text in [d["solution"], *d["hints"]]:
        problem = _lint_text(text)
        if problem:
            return problem
    return None


def _ngrams(text, n):
    w = re.findall(r"\w+", text.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def leak(d, inp, n=8):
    """No public field may share wording or numbers with the source. The gate reads only the statement."""
    source = _ngrams(inp.statement, n)
    for name in ("title", "statement", "sketch", "solution"):
        if _ngrams(d.get(name, ""), n) & source:
            return f"the {name} repeats wording from the source problem"
    if any(_ngrams(h, n) & source for h in d.get("hints", [])):
        return "a hint repeats wording from the source problem"
    nums = lambda t: set(re.findall(r"(?<![\d.])\d{2,}(?![\d.])", t)) - {"10", "100", "1000"}
    src, new = nums(inp.statement), nums(d["statement"])
    if len(src & new) >= 2 and len(src & new) * 2 >= len(src):
        return "the statement reuses the source problem's numbers"
    return None


def run_program(src):
    """What the program prints, for free: returns (key, None) or (None, reason)."""
    reason, hard_coded = sandbox.static_check(src)
    if reason:
        return None, f"check_program rejected: {reason}"
    if hard_coded:
        return None, "check_program hard-codes its answer: it computes nothing"
    result = sandbox.run_program(src)
    if not result.ok:
        return None, f"check_program didn't finish: {result.error}"
    lines = [x for x in result.stdout.strip().splitlines() if x.strip()]
    return (answers.tidy(lines[-1].strip()) if lines else ""), None


def idea_checks(idea, inp, index, threshold):
    """Everything free about an idea, so a bad one costs nothing. Returns (step, reason, key)."""
    problem = lint_idea(idea)
    if problem:
        return "idea_lint", problem, None
    problem = leak(idea, inp)
    if problem:
        return "leak", problem, None
    status, reason, _ = originality.lexical(dict(id="?", statement=idea["statement"]), index, threshold)
    if status == "fail":
        return "originality_lexical", reason, None
    key, reason = run_program(idea["check_program"])
    if reason:
        return "program", reason, None
    problem = lint_key(idea, key)
    if problem:
        return "key", problem, key
    if inp.answer and answers.canon(inp.answer) == answers.canon(key):
        return "key", "the key equals the source problem's answer", key
    return None, None, key


def write_checks(d, inp):
    """The free checks on a finished draft. The gate repeats the ones it owns. Returns (step, reason) or None."""
    status, reason, _ = schema_check.run(d)
    if status == "fail":
        return "schema", reason
    status, reason, _ = standard.run(d)
    if status == "fail":
        return "standard", reason
    problem = lint(d)
    if problem:
        return "lint", problem
    problem = leak(d, inp)
    if problem:
        return "leak", problem
    return None
