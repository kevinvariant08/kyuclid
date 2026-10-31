"""Checks 4 and 5: the well-posedness critic and the solution audit."""
from . import prompts
from .backend import last_json
from .config import ROLES


def _material(items):
    return [str(x.get("issue", x)) for x in items or [] if not isinstance(x, dict) or x.get("severity") != "cosmetic"]


def well_posedness(draft, backend, usage):
    model, effort, cap = ROLES["well_posedness"]
    r = backend.call(model, prompts.WELL_POSED, prompts.well_posed(draft), effort, cap, role="well_posedness", draft_id=draft["id"])
    usage.add(r)
    d = last_json(r.text)
    if d is None:
        return "fail", f"critic reply unreadable: {r.text[:120]}", {"model": r.model}
    ev = {"model": r.model, "findings": d.get("findings", [])}
    bad = _material(d.get("findings"))
    if bad:
        return "fail", bad[0], ev
    return "pass", "no material findings", ev


def figure_critic(draft, renders, backend, usage):
    """The figure check proves the figure agrees with itself. Only a reader looking at it can say it shows this problem."""
    model, effort, cap = ROLES["figure_critic"]
    r = backend.call(model, prompts.FIGURE_CRITIC, prompts.figure_critic(draft), effort, cap, role="figure_critic", draft_id=draft["id"], images=renders)
    usage.add(r)
    d = last_json(r.text)
    if d is None:
        return "fail", f"critic reply unreadable: {r.text[:120]}", {"model": r.model}
    ev = {"model": r.model, "findings": d.get("findings", [])}
    bad = _material(d.get("findings"))
    if bad:
        return "fail", bad[0], ev
    return "pass", "the figure shows this solution's configuration, and it reads clearly", ev


def solution_audit(draft, backend, usage):
    model, effort, cap = ROLES["solution_audit"]
    r = backend.call(model, prompts.AUDIT, prompts.audit(draft), effort, cap, role="solution_audit", draft_id=draft["id"])
    usage.add(r)
    d = last_json(r.text)
    if d is None:
        return "fail", f"critic reply unreadable: {r.text[:120]}", {"model": r.model}
    ev = {"model": r.model, "reaches_answer": d.get("reaches_answer"), "issues": d.get("issues", [])}
    bad = _material(d.get("issues"))
    if bad:
        return "fail", bad[0], ev
    if not d.get("reaches_answer"):
        return "fail", "the solution doesn't reach the stated answer", ev
    return "pass", "every step justified and the answer reached", ev
