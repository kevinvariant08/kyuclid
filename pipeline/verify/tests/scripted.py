"""A backend that answers from a script, so the verdict logic can be tested for free and without a network."""
import json

from ..backend import Backend, Reply


class ScriptedBackend(Backend):
    """Behaves as a well-behaved model would: right answers, no findings. A draft's `sim` entry overrides that."""

    def __init__(self, drafts=None, sims=None):
        super().__init__(concurrency=8, name="scripted", use_cache=False)
        self.drafts, self.sims = drafts or {}, sims or {}
        self.prompts = []

    def _send(self, model, system, prompt, effort, max_tokens, role, draft_id, salt):
        self.prompts.append((role, draft_id, prompt))
        sim = self.sims.get(draft_id, {})
        tokens = 900
        if role == "solve":
            i = int(salt.split("-")[1])
            answers = sim.get("solves") or [self.drafts[draft_id]["answer"]] * 7
            text = f'Working.\n{{"answer":"{answers[i]}"}}'
            tokens = sim.get("solve_tokens", 900)
        elif role == "program_judge":
            text = json.dumps(sim.get("program", {"verdict": "computes", "reason": "it enumerates"}))
        elif role == "well_posedness":
            text = json.dumps({"findings": sim.get("wellposed", [])})
        elif role == "solution_audit":
            text = json.dumps(sim.get("audit", {"reaches_answer": True, "issues": []}))
        elif role == "originality":
            text = json.dumps(sim.get("originality", {"neighbours": [], "known": {"is_known": False, "name": "", "reason": ""}}))
        else:
            text = "An abstract idea."
        return Reply(text=text, model=model, input=100, output=tokens, thinking=tokens // 2, usd=0.001)
