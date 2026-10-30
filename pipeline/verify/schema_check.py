"""Check 1: the draft matches the site's schema, its key matches its hash, and its LaTeX compiles."""
import json
import re
import subprocess

from jsonschema import Draft202012Validator

from . import answers
from .config import GATE_FIELDS, HERE, SCHEMA

TEX_DRY_RUN = HERE / "js" / "tex_dry_run.mjs"
_validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))


def strip_gate_fields(draft):
    return {k: v for k, v in draft.items() if k not in GATE_FIELDS}


def _texts(p):
    for name in ("statement", "solution"):
        yield name, p.get(name, "")
    for i, h in enumerate(p.get("hints", [])):
        yield f"hints[{i}]", h
    for i, r in enumerate(p.get("rubric", [])):
        yield f"rubric[{i}]", r.get("criterion", "")


def split_math(text):
    """Returns (snippets, problem). A snippet is (tex, display). Unbalanced delimiters are the problem."""
    out, i, n = [], 0, len(text)
    while i < n:
        if text[i] == "\\" and i + 1 < n and text[i + 1] == "$":
            i += 2
        elif text.startswith("$$", i):
            j = text.find("$$", i + 2)
            if j < 0:
                return out, "unclosed $$"
            out.append((text[i + 2:j], True))
            i = j + 2
        elif text[i] == "$":
            j = i + 1
            while j < n and (text[j] != "$" or text[j - 1] == "\\"):
                j += 1
            if j >= n:
                return out, "unclosed $"
            out.append((text[i + 1:j], False))
            i = j + 1
        else:
            i += 1
    return out, None


def _balanced(tex):
    depth = 0
    for m in re.finditer(r"\\.|[{}]", tex, re.S):
        if m.group() == "{":
            depth += 1
        elif m.group() == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def check_latex(draft):
    """Returns (engine, errors). The engine is mathjax, or balance-only if mathjax-full isn't installed."""
    errors, snippets = [], []
    for name, text in _texts(draft):
        found, problem = split_math(text)
        if problem:
            errors.append(f"{name}: {problem}")
        for tex, display in found:
            if not _balanced(tex):
                errors.append(f"{name}: unbalanced braces in ${tex[:40]}$")
            snippets.append((name, tex, display))
    p = subprocess.run(["node", str(TEX_DRY_RUN)], input=json.dumps([{"tex": t, "display": d} for _, t, d in snippets]),
                       capture_output=True, text=True, encoding="utf-8")
    if p.returncode == 3:
        return "balance-only (run npm ci for the MathJax dry run)", errors
    if p.returncode != 0:
        return "balance-only (MathJax failed to run)", errors + [f"tex_dry_run: {p.stderr[:200]}"]
    for (name, tex, _), err in zip(snippets, json.loads(p.stdout)):
        if err:
            errors.append(f"{name}: {err} in ${tex[:40]}$")
    return "mathjax", errors


def run(draft):
    errs = sorted(_validator.iter_errors(strip_gate_fields(draft)), key=lambda e: list(map(str, e.path)))
    if errs:
        msgs = [f"{'/'.join(map(str, e.path)) or '(top level)'}: {e.message[:120]}" for e in errs[:5]]
        return "fail", "; ".join(msgs), {"errors": msgs}
    ev = {}
    if draft["type"] == "answer":
        if "answer" not in draft or "check_program" not in draft:
            return "fail", "an answer draft needs answer and check_program", ev
        if answers.canon(draft["answer"]) is None:
            return "fail", f'answer "{draft["answer"]}" isn\'t a number, a decimal or a fraction, so the site can\'t check it', ev
        if answers.answer_hash(draft["id"], draft["answer"]) != draft["answer_hash"]:
            return "fail", "answer_hash doesn't match answer", ev
    engine, latex = check_latex(draft)
    ev["latex_engine"] = engine
    if latex:
        return "fail", "LaTeX: " + "; ".join(latex[:3]), {**ev, "errors": latex}
    return "pass", f"schema valid, LaTeX compiled ({engine})", ev
