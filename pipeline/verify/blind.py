"""Check 3: seven independent solves from the statement alone."""
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from statistics import median

from . import answers, prompts
from .backend import last_json
from .config import PASS_SOLVES, ROLES, SOLVERS, SONNET


def _extract(text):
    d = last_json(text)
    if d and "answer" in d:
        return str(d["answer"])
    m = re.findall(r"\\boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", text)
    return m[-1] if m else ""


def solve_all(statement_draft, backend, usage, cacheable=True):
    """statement_draft needs only id, statement and optionally figure_alt, so nothing else can leak in."""
    _, effort, cap = ROLES["solve"]
    prompt = prompts.solve(statement_draft)

    def one(i_model):
        i, model = i_model
        r = backend.call(model, prompts.SOLVE, prompt, effort, cap, salt=f"solve-{i}", cacheable=cacheable, role="solve", draft_id=statement_draft["id"])
        usage.add(r)
        return dict(model=r.model, answer=answers.tidy(_extract(r.text)), output_tokens=r.output, reasoning_tokens=r.thinking, truncated=r.truncated)

    with ThreadPoolExecutor(len(SOLVERS)) as pool:
        solves = list(pool.map(one, enumerate(SOLVERS)))
    for s, c in zip(solves, answers.canon_many([s["answer"] for s in solves])):
        s["canon"] = c
    return solves


def analyse(draft, solves, too_easy_tokens):
    key = answers.canon(draft["answer"])
    right = sum(s["canon"] == key for s in solves)
    sonnet = [s["output_tokens"] for s in solves if s["model"] == SONNET]
    tokens = median(sonnet) if sonnet else 0
    groups = Counter(s["canon"] for s in solves if s["canon"] is not None)
    top, top_n = groups.most_common(1)[0] if groups else (None, 0)
    ev = dict(solves=solves, right=right, total=len(solves), median_sonnet_tokens=tokens, groups=dict(groups))
    if right == len(solves) and tokens <= too_easy_tokens and draft["kyu"] <= 5:
        return "fail", f"too easy for {draft['kyu']} kyu: {right}/{len(solves)} solved it at about {tokens:.0f} tokens", ev
    if right >= PASS_SOLVES:
        return "pass", f"{right}/{len(solves)} blind solves agree with the key", ev
    if top_n >= PASS_SOLVES and top != key:
        return "investigate", f"wrong key or ambiguous: {top_n}/{len(solves)} agree on {top}, the key is {draft['answer']}", ev
    return "investigate", f"only {right}/{len(solves)} reach the key and no majority agrees: too hard, or ambiguous", ev
