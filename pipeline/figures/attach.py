"""Attaches built figures to problems, by id, using figures/index.json.

python -m pipeline.figures attach                     published problems in data/problems
python -m pipeline.figures attach --dir review/pending --dir review/approved    review files too
python -m pipeline.figures attach --dry-run           say what would change and write nothing

A review file also gets figure_sources, so the draft carries its own .tex and .svg between checkouts. A problem
whose solution has since been edited down to fewer paragraphs is reported and left alone.
"""
import json
import re
from pathlib import Path

from .build import FIGURES, ROOT, figure_paths

INDEX = FIGURES / "index.json"
BANK = ROOT / "data" / "problems"


def paragraphs(solution):
    return len(re.split(r"\n\s*\n", solution))


def sources_for(figures):
    out = []
    for f in figures:
        name = f["src"].split("?")[0][len("figures/"):-len(".svg")]
        tex, svg = figure_paths(name)
        out.append(dict(name=name, tex=tex.read_text(encoding="utf-8"), svg=svg.read_text(encoding="utf-8")))
    return out


def attach_to(draft, figures, carry_sources):
    """Returns the changed draft, or raises ValueError if the figures no longer fit its solution."""
    count = paragraphs(draft["solution"])
    for f in figures:
        if f["after_paragraph"] > count:
            raise ValueError(f"{f['src']} goes after paragraph {f['after_paragraph']}, but the solution now has {count}")
    changed = {**draft, "solution_figures": figures}
    if carry_sources:
        changed["figure_sources"] = sources_for(figures)
    return changed


def _write(path, data, trailing_newline=True):
    path.write_bytes((json.dumps(data, indent=2, ensure_ascii=False) + ("\n" if trailing_newline else "")).encode("utf-8"))


def run_attach(args):
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    found, problems = set(), 0
    for pid, figures in index.items():
        bank_file = BANK / f"{pid}.json"
        if bank_file.exists():
            found.add(pid)
            draft = json.loads(bank_file.read_text(encoding="utf-8"))
            try:
                changed = attach_to(draft, figures, carry_sources=False)
            except ValueError as e:
                print(f"{pid}: NOT ATTACHED: {e}")
                problems += 1
                continue
            if changed != draft:
                print(f"{pid}: {len(figures)} figure(s) attached in data/problems")
                if not args.dry_run:
                    _write(bank_file, changed)
        for folder in args.dir:
            path = Path(folder) / f"{pid}.json"
            if not path.exists():
                continue
            found.add(pid)
            record = json.loads(path.read_text(encoding="utf-8"))
            wrapped = "draft" in record
            draft = record["draft"] if wrapped else record
            try:
                changed = attach_to(draft, figures, carry_sources=True)
            except ValueError as e:
                print(f"{pid}: NOT ATTACHED in {folder}: {e}")
                problems += 1
                continue
            if changed != draft:
                print(f"{pid}: {len(figures)} figure(s) attached in {folder}")
                if not args.dry_run:
                    _write(path, {**record, "draft": changed} if wrapped else changed, trailing_newline=False)
    missing = sorted(set(index) - found)
    if missing:
        print(f"Not found, so nothing done for: {', '.join(missing)}")
    return 1 if problems else 0


def add_arguments(p):
    p.add_argument("--dir", action="append", default=[], help="A review folder of <id>.json files. Repeat for several.")
    p.add_argument("--dry-run", action="store_true")
