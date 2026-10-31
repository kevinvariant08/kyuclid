"""The figure check: a solution that argues from a picture has a figure, and the figure is right.

Free. It compiles each figure afresh, re-checks its facts and layout, and looks for the numbers its facts claim in
the draft's own text, because a figure could be perfectly consistent and still show another problem.
A machine without TeX gets ERROR, not a verdict: that says nothing about the draft.
"""
import re
from pathlib import Path

from ..figures.build import ToolchainError, build_source, figure_paths
from ..figures.source import Figure, FigureError, fact_numbers

# For non-geometry topics: wording that says the argument works on a picture. figure_exempt answers it with a reason.
PICTURE_WORDS = re.compile(r"complex plane|coordinate plane|as points? in the plane|\bchords?\b|\bparabola\b|\bellipse\b|\bhyperbola\b|\bcircumcircle\b|\bpolygon\b|\b\d*-?gon\b|tangent to", re.I)


def needs_figure(draft):
    if draft.get("topic") == "G":
        return "a geometry solution needs a figure"
    if draft.get("figure_exempt"):
        return None
    if PICTURE_WORDS.search(draft.get("solution", "")) or PICTURE_WORDS.search(draft.get("statement", "")):
        return "this solution seems to argue from a picture, so it needs a figure, or a figure_exempt reason if it doesn't"
    return None


def _sources(draft):
    """[(name, tex, committed svg or None)]. A draft carries its own, and a backfilled one is on disk."""
    carried = {s["name"]: s for s in draft.get("figure_sources", [])}
    out = []
    for f in draft.get("solution_figures", []):
        name = f["src"].split("?")[0][len("figures/"):-len(".svg")]
        if name in carried:
            out.append((name, carried[name]["tex"], carried[name].get("svg")))
        else:
            tex, svg = figure_paths(name)
            if not tex.exists():
                raise FigureError(f"{name}: no .tex source, in the draft or in figures/")
            out.append((name, tex.read_text(encoding="utf-8"), svg.read_text(encoding="utf-8") if svg.exists() else None))
    return out


def _plain_numbers(text):
    """The draft's text with fractions written a/b, so 25/4 in a fact matches \\frac{25}{4} in the solution."""
    t = re.sub(r"\\[dt]?frac\s*\{\s*(\d+)\s*\}\s*\{\s*(\d+)\s*\}", r"\1/\2", text)
    return re.sub(r"\\[,!;:]|\s", "", t)


def _grounded(figure, draft):
    text = _plain_numbers(draft.get("statement", "") + " " + draft.get("solution", ""))
    for fact, number in fact_numbers(figure):
        if not re.search(rf"(?<![\d.]){re.escape(number)}(?![\d.])", text):
            return f"{fact} isn't in the statement or solution. If the figure draws one example case, say %! example instead of %! fact"
    return None


def run(draft, render_dir=None):
    """Returns (status, reason, evidence). PNGs go to render_dir for the critic, listed in evidence["renders"]."""
    ev = dict(figures=[], renders=[])
    figures = draft.get("solution_figures") or []
    if not figures:
        why = needs_figure(draft)
        return ("fail", why, ev) if why else ("pass", "no figure needed", ev)

    paragraphs = re.split(r"\n\s*\n", draft["solution"])
    limit = len(paragraphs) - 1 if paragraphs[-1].lstrip().startswith("<b>Why this works") else len(paragraphs)
    total = 0
    try:
        for f, (name, tex, svg) in zip(figures, _sources(draft)):
            if f["after_paragraph"] > limit:
                return "fail", f"{name}: after_paragraph is {f['after_paragraph']}, but the argument has {limit} paragraphs", ev
            png = Path(render_dir) / f"{name}.png" if render_dir else None
            built = build_source(name, tex, render_png=png)
            if built.layout:
                return "fail", f"{name}: {built.layout[0]}", {**ev, "layout": built.layout}
            problem = _grounded(Figure(name, tex), draft)
            if problem:
                return "fail", f"{name}: {problem}", ev
            if svg is None or svg.replace("\r\n", "\n") != built.svg or not f["src"].endswith("?v=" + built.version):
                return "fail", f"{name}: the SVG on file isn't what this source compiles to. Rebuild it: python -m pipeline.figures build", ev
            total += built.facts
            ev["figures"].append(dict(name=name, facts=built.facts))
            if png:
                ev["renders"].append(str(png))
    except FigureError as e:
        return "fail", f"figure: {e}", ev
    except ToolchainError as e:
        return "error", str(e), ev
    return "pass", f"{len(figures)} figure(s) compiled, {total} facts held", ev
