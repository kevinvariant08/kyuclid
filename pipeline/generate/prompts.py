"""The generator's prompts. Replies use tags, not JSON: LaTeX and Python both break JSON escaping constantly.

Two stages, because three full candidates worked out by hand used up a 32,000-token cap with nothing written:
ideas (statement and program, for three candidates), then a write-up of the chosen one. The sandbox computes
each key for free, so the model spends its effort on the idea and not on arithmetic.
"""
import json
import re

from ..verify.sandbox import ALLOWED_IMPORTS
from .config import STANDARD, TAXONOMY
from .recipes import RECIPES

SYSTEM = ("You write original maths contest problems for Kyuclid, a site ranked from 8 kyu (beginner) to 1 kyu (IMO). "
          "A good problem gives the solver one real moment of insight, reads naturally and is exactly right. "
          "You have no tools. Output only what the format asks for. "
          "Your thinking budget is small: stop thinking after about 1,500 words and start writing. Independent checks run on everything you write and "
          "send back anything wrong, so a good first idea written down beats a perfect one still being tested. Never test parameters or compute answers in your head.")

WRITE_SYSTEM = ("You write hints and solutions for Kyuclid, a maths contest site. You have no tools. Output only what the format asks for. "
                "Your thinking budget is small: stop thinking after about 1,500 words and start writing.")

IDEA_FORMAT = """<candidate>
<title>A short title that gives nothing away: no technique, theorem or answer.</title>
<recipe>{recipes}</recipe>
<topic>One of A, C, G, N.</topic>
<statement>The statement.</statement>
<sketch>The intended solution in at most five lines: the crux and the route. No full working.</sketch>
<check_program>Python source. No markdown fence.</check_program>
<interest>Your honest rating of how interesting this is, from 1 to 10.</interest>
<interest_reason>One sentence.</interest_reason>
</candidate>"""

WRITE_FORMAT = """<subtopics>Taxonomy IDs separated by commas, the one the crux turns on first.</subtopics>
<hint>Hint 1.</hint>
<hint>Hint 2.</hint>
<hint>Hint 3 (optional).</hint>
<solution>The solution, ending with the "Why this works" paragraph.</solution>"""

STYLE = """THE STYLE TO AIM FOR
The problem should read and feel like a real AIME problem: a short, clean statement, no contrived story, one satisfying crux, and an integer answer from 0 to 999, encoded as $m + n$ or similar where the AIME would do that. Use the same kinds of ideas and the same difficulty curve. Sharing an idea family with AIME problems is the goal. Copying is not: never reuse a specific problem's setting, numbers or phrasing, and never write a reskin."""

IDEA_RULES = """How your work is checked. Every point here has rejected real drafts.
- Do not work out the answer by hand. A sandbox runs your program and its output becomes the key, so spend your thought on the idea and on making the statement exact. Keep your reasoning short.
- The key must be an integer from 2 to 999 and must not appear as a number in the statement. Choose the statement's parameters, or ask for a remainder modulo $1000$ or an encoding such as $m + n$ (rule A4), so that this holds. Do not make the encoding the hard part.
- check_program computes the actual quantity from the problem's own definitions: enumerate, search or do exact symbolic work, using exact coordinates for geometry. A judge rejects a program that evaluates a closed formula from the solution, searches a smaller case and then applies a formula, or contains the answer. It must finish within 30 seconds and print only the key on its last line, as a plain integer.
- check_program may import only: {imports}. Never use random, files or the network.
- A strict critic reads the statement for anything a competent solver could read two ways. Define every object, say whether integers are positive, whether pairs are ordered, whether a set may be empty, and whether points lie on sides or on lines. Avoid informal shorthand such as "uses the letters A, B and C"; state exactly what is meant.
- Seven models then solve it blind from the statement alone. Do not rely on a figure: describe every point and condition in words.
- A judge compares it with the source problem and other published problems. It rejects any problem with the same structure and solution path, whatever the setting or numbers, and any well-known problem. A solver who knows the source must still have to think of something new.
- All text uses UK spelling. Use $...$ and $$...$$ for maths, with no custom macros."""

WRITE_RULES = """How your work is checked.
- A strict auditor reads the solution. Justify every non-routine step and every case. Routine algebra may be skipped. It must state the key in the second-last paragraph, and the "Why this works" paragraph follows it as the last paragraph.
- The key comes from a program, so a solution that reaches any other number is wrong. Work it out honestly. If you find the key or the statement is wrong, reply with only <disagree>one sentence on what is wrong</disagree> instead of bending the argument.
- No hint may state the key. Each hint adds something, and the last stops one routine step short.
- All text uses UK spelling. Use $...$ and $$...$$ for maths: \\dfrac in display maths and \\frac inline, always with braces, \\cdot for products and never *, \\le and \\ge. Use only <b> and <code> as markup.
- The solution's last paragraph is exactly: <b>Why this works.</b> <code>id-one</code>, <code>id-two</code>: one clause on why the idea fits. Each ID must also be in subtopics."""


def _section(text, start, end):
    i = text.index(start)
    return text[i:text.index(end, i + 1)]


def _standard():
    return STANDARD.read_text(encoding="utf-8")


def idea_rules(kyu):
    """The standard's own words, so a change there reaches the generator with no edit here."""
    text = _standard()
    lines = _section(text, "### 1.4 The ladder", "### 1.5 Examples").splitlines()
    ladder = next(x for x in lines if x.startswith(f"| {kyu} |"))
    header = next(x for x in lines if x.startswith("| Kyu | Belt |"))
    return "\n\n".join([_section(text, "### 1.3 Definitions", "### 1.4 The ladder"), f"The target rung:\n{header}\n{ladder}",
                        _section(text, "## 2. Statement rules", "## 4. Solution rules"), _section(text, "## 6. What makes a problem bad", "## 8. Proof problems")])


def write_rules():
    return _section(_standard(), "## 4. Solution rules", "## 6. What makes a problem bad")


def taxonomy_ids():
    t = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    return ", ".join(x["id"] for x in t["techniques"] + t["configurations"] if x.get("status") != "legacy")


def describe_record(record):
    paths = "\n".join(f"- {p.get('name')} ({p.get('difficulty_of_path')}): {'; '.join(p.get('key_steps') or [])}" for p in record.get("solution_paths") or [])
    return (f"Core idea: {record.get('core_idea')}\nCrux: {record.get('crux')}\nTechniques: {', '.join(record.get('techniques') or [])}\n"
            f"Solution routes:\n{paths}\nTraps: {'; '.join(record.get('traps') or [])}\nNote on using it: {record.get('generation_note') or 'none'}")


def _idea_context(inp, kyu, digest):
    parts = [
        f"Write for {kyu} kyu. Its difficulty must come from an idea, not from arithmetic.",
        STYLE,
        f"THE KYUCLID STANDARD\n{idea_rules(kyu)}",
        IDEA_RULES.format(imports=", ".join(sorted(ALLOWED_IMPORTS))),
        f"THE IDEA TO TEACH\n{describe_record(inp.record)}",
        ("THE SOURCE PROBLEM, for calibration only. It shows how hard the target is. Do not reuse its setting, objects, numbers or phrasing, "
         f"and never mention it.\n<<<\n{inp.statement}\n>>>"),
    ]
    if digest:
        parts.append(f"WHAT THE HUMAN REVIEWER HAS BEEN REJECTING\n{digest}")
    return parts


def ideas(inp, kyu, recipes, partner=None, digest=""):
    lines = [f"- {name}: {RECIPES[name]}" for name in recipes]
    if "combine" in recipes and partner:
        lines.append(f"The second technique for combine: {partner}. It rarely appears with this idea at this kyu.")
    if "change-route" in recipes:
        lines.append("For change-route, use a route other than the first one listed above.")
    n = len(recipes)
    return "\n\n".join(_idea_context(inp, kyu, digest) + [
        f"YOUR TASK\nWrite {n} candidates, one for each recipe below. A pure number swap, or the same story with renamed objects, is never acceptable.\n" + "\n".join(lines),
        "OUTPUT\n" + IDEA_FORMAT.format(recipes=" or ".join(recipes)) + f"\nRepeat that block {n} times, with nothing else around it.",
    ])


def idea_repair(inp, kyu, previous, failure, digest=""):
    shown = "\n".join(f"<{k}>{previous[k]}</{k}>" for k in ("title", "statement", "sketch", "check_program"))
    return "\n\n".join(_idea_context(inp, kyu, digest) + [
        f"YOUR EARLIER CANDIDATE, using the recipe {previous['recipe']}\n{shown}",
        (f"WHY IT WAS REJECTED\n{failure}\n\nFix the cause, not the symptom. If the statement and program disagree, correct whichever is wrong. "
         "If it was too close to another problem, change what the solver has to do: changing the setting or the numbers will fail again."),
        "OUTPUT\n" + IDEA_FORMAT.format(recipes=previous["recipe"]) + "\nWrite that block once, with nothing else around it.",
    ])


def write_up(idea, kyu, key, record, earlier=None, failure=None):
    """Has no contest text in it: the source isn't needed here, so it can't be copied here."""
    parts = [
        f"A {kyu} kyu problem has been chosen. Write its hints and solution.",
        f"THE KYUCLID STANDARD\n{write_rules()}",
        WRITE_RULES,
        f"TAXONOMY IDS, the only tags allowed\n{taxonomy_ids()}",
        f"THE PROBLEM\n{idea['statement']}\n\nTHE KEY, computed by a program: {key}\n\nTHE PROGRAM\n{idea['check_program']}\n\nTHE AUTHOR'S SKETCH\n{idea.get('sketch', '')}",
    ]
    if earlier and failure:
        parts.append(f"YOUR EARLIER WRITE-UP\n{earlier}\n\nWHY IT WAS REJECTED\n{failure}")
    parts.append("OUTPUT\n" + WRITE_FORMAT + "\nNothing else around it.")
    return "\n\n".join(parts)


def _tag(block, name):
    m = re.search(rf"<{name}>(.*?)</{name}>", block, re.S)
    return m.group(1).strip() if m else ""


def parse_ideas(text):
    """Returns the candidates that have every required part. A truncated last block is simply dropped."""
    out = []
    for block in re.findall(r"<candidate>(.*?)</candidate>", text, re.S):
        c = {k: _tag(block, k) for k in ("title", "recipe", "topic", "statement", "sketch", "check_program", "interest_reason")}
        c["check_program"] = re.sub(r"^```\w*\n|\n?```$", "", c["check_program"])
        m = re.search(r"\d+(\.\d+)?", _tag(block, "interest"))
        c["interest"] = float(m.group()) if m else 0.0
        if all(c[k] for k in ("title", "statement", "check_program")):
            out.append(c)
    return out


def parse_write_up(text):
    """Returns the write-up's fields, or a dict with only disagree, or None if it's incomplete."""
    disagree = _tag(text, "disagree")
    if disagree:
        return dict(disagree=disagree)
    w = dict(subtopics=[s.strip() for s in _tag(text, "subtopics").split(",") if s.strip()], solution=_tag(text, "solution"),
             hints=[h.strip() for h in re.findall(r"<hint>(.*?)</hint>", text, re.S) if h.strip()])
    return w if w["solution"] and w["hints"] and w["subtopics"] else None
