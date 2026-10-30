"""Check 8: the automatable rules from tasks/04-problem-standard.md.

docs/problem-standard.md doesn't exist yet. When task 04 lands, compare this list with its appendix of automatable rules.
"""
import re

from . import answers

US_TO_UK = {"color": "colour", "colored": "coloured", "coloring": "colouring", "colors": "colours", "neighbor": "neighbour", "neighbors": "neighbours",
            "neighboring": "neighbouring", "center": "centre", "centers": "centres", "centered": "centred", "favorite": "favourite", "gray": "grey",
            "analyze": "analyse", "behavior": "behaviour", "labeled": "labelled", "meter": "metre", "meters": "metres", "liter": "litre", "liters": "litres",
            "centimeter": "centimetre", "centimeters": "centimetres", "kilometer": "kilometre", "kilometers": "kilometres", "millimeter": "millimetre",
            "honor": "honour", "rumor": "rumour", "theater": "theatre", "catalog": "catalogue", "traveling": "travelling", "canceled": "cancelled",
            "factorize": "factorise", "minimize": "minimise", "maximize": "maximise", "organize": "organise", "recognize": "recognise"}
CONTESTS = r"\b(AIME|AMC|USAMO|USAJMO|UKMT|BMO|IMO|ISL|EGMO|CGMO|APMO|RMM|HMMT|ARML|PUMaC|CMIMC|SMT)\b"


def _prose(text):
    return re.sub(r"\$\$.*?\$\$|\$[^$]*\$", " ", text, flags=re.S)


def run(draft):
    fails, warns = [], []
    fields = [draft["statement"], draft["solution"], *draft["hints"]]
    n = len(draft["hints"])
    if draft["type"] == "answer":
        if n < 2:
            fails.append(f"hint count: {n}, the standard asks for two or three")
        a = answers.canon(draft["answer"])
        value = float(a) if a is not None else None
        fmt = draft.get("answer_format")
        if value is not None:
            if draft["kyu"] in (5, 4, 3) and not (value == int(value) and 0 <= value <= 999):
                fails.append(f"answer range: {draft['kyu']} kyu answers are integers from 0 to 999, got {draft['answer']}")
            if fmt == "integer_0_999" and not (value == int(value) and 0 <= value <= 999):
                fails.append(f"answer format: integer_0_999 but the answer is {draft['answer']}")
            if fmt == "integer" and value != int(value):
                fails.append(f"answer format: integer but the answer is {draft['answer']}")
            if value in (0, 1):
                warns.append("answer is 0 or 1, which is guessable")
        word = re.escape(str(draft["answer"]))
        for i, h in enumerate(draft["hints"]):
            if len(str(draft["answer"])) >= 2 and re.search(rf"(?<![\d.]){word}(?![\d.])", h):
                fails.append(f"hint {i + 1} gives away the answer")
        if not re.search(rf"(?<![\d.]){word}(?![\d.])", draft["solution"]):
            warns.append("the solution never states the answer in that form")
    if n > 1 and len(draft["hints"][-1]) < len(draft["hints"][0]) * 0.5:
        warns.append("hint order: the last hint is much shorter than the first, so check they get stronger")
    for text in fields:
        for w in re.findall(r"[A-Za-z]+", _prose(text)):
            uk = US_TO_UK.get(w.lower())
            if uk:
                fails.append(f'UK spelling: "{w}" should be "{uk}"')
    if draft.get("provenance", {}).get("kind") == "original":
        for text in fields:
            m = re.search(CONTESTS, _prose(text))
            if m:
                fails.append(f"an original problem names the contest {m.group(1)}")
    if draft.get("inspired_by") and any(draft["inspired_by"] in t for t in fields):
        fails.append("the public text mentions its private inspired_by ID")
    fails = list(dict.fromkeys(fails))
    ev = {"failures": fails, "warnings": warns}
    if fails:
        return "fail", fails[0] + (f" (and {len(fails) - 1} more)" if len(fails) > 1 else ""), ev
    return "pass", "automatable standard rules hold" + (f"; warnings: {'; '.join(warns)}" if warns else ""), ev
