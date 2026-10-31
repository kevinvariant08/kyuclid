"""Check 2: check_program must compute the answer itself, in the sandbox, without restating the solution."""
from . import answers, prompts, sandbox
from .backend import last_json
from .config import ROLES


def run_program_check(draft, seconds=None):
    src, key = draft["check_program"], draft["answer"]
    reason, hard_coded = sandbox.static_check(src)
    if reason:
        return "fail", f"check_program rejected: {reason}", {}
    if hard_coded or sandbox.prints_literal(src, key):
        return "fail", "check_program hard-codes its answer (static check: it computes nothing)", {"static_hard_coded": True}
    run = sandbox.run_program(src, seconds)
    if not run.ok:
        return "fail", f"check_program didn't finish: {run.error}", {"error": run.error}
    lines = [x for x in run.stdout.strip().splitlines() if x.strip()]
    got = lines[-1].strip() if lines else ""
    ev = {"program_output": got}
    if answers.canon(answers.tidy(got)) != answers.canon(key):
        return "fail", f"check_program prints {got or '(nothing)'} but the key is {key}", ev
    return "pass", "check_program output matches the key", ev


def judge(draft, backend, usage):
    model, effort, cap = ROLES["program_judge"]
    r = backend.call(model, prompts.PROGRAM_JUDGE, prompts.program_judge(draft), effort, cap, role="program_judge", draft_id=draft["id"])
    usage.add(r)
    d = last_json(r.text) or {}
    verdict = str(d.get("verdict", "")).lower()
    ev = {"judge": {"model": r.model, "verdict": verdict, "reason": d.get("reason", "")}}
    if verdict == "computes":
        return "pass", "check_program independently computes the answer", ev
    if verdict in ("hardcoded", "restates", "wrong_problem"):
        return "fail", f"judge says check_program {verdict}: {d.get('reason', '')}", ev
    return "fail", f"judge reply unreadable: {r.text[:120]}", ev
