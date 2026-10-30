"""Check 6: blind-solve rate and token use mapped to a kyu, with thresholds fitted by fit_difficulty.py."""
import json
import math

from .config import HERE

THRESHOLDS = HERE / "thresholds.json"


def load():
    return json.loads(THRESHOLDS.read_text(encoding="utf-8"))


def score(right, total, tokens):
    """Higher is harder. Each doubling of the tokens counts 1; every solver who fails counts 0.75."""
    return math.log2(max(tokens, 100) / 100) + 0.75 * (total - right)


def estimate(s, cuts):
    """cuts lists {kyu, max_score} from easiest to hardest. Anything past the last cut is one kyu harder."""
    for c in cuts:
        if s <= c["max_score"]:
            return c["kyu"]
    return max(cuts[-1]["kyu"] - 1, 1)


def run(draft, blind_ev, th):
    s = score(blind_ev["right"], blind_ev["total"], blind_ev["median_sonnet_tokens"])
    est = estimate(s, th["cuts"])
    ev = dict(score=round(s, 2), estimated_kyu=est, target_kyu=draft["kyu"], provisional=th.get("provisional", False), fitted_on=th.get("fitted_on"))
    msg = f"estimated {est} kyu, target {draft['kyu']} kyu"
    if abs(est - draft["kyu"]) <= 1:
        return "pass", msg, ev
    # A rough ruler shouldn't reject a draft outright: until the full fit it only asks a human to look.
    if th.get("provisional"):
        return "investigate", msg + " (thresholds are provisional)", ev
    return "fail", msg, ev
