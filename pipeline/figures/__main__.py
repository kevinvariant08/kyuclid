"""The one script that builds figures.

python -m pipeline.figures sync <name>...     fill in the decimals from the exact values
python -m pipeline.figures build [name...]    sync, check and compile to figures/<name>.svg, and rewrite figures/index.json
python -m pipeline.figures check              what CI-with-TeX would run: nothing may differ from the committed files
python -m pipeline.figures attach ...         see attach.py
"""
import argparse
import json
import sys

from .attach import add_arguments, run_attach
from .build import FIGURES, ToolchainError, all_names, build_source, figure_paths, problem_id, svg_version
from .source import Figure, FigureError

INDEX = FIGURES / "index.json"


def write_lf(path, text):
    path.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))


def sync(names):
    for name in names:
        tex_path, _ = figure_paths(name)
        text = Figure(name, tex_path.read_text(encoding="utf-8")).synced_tex()
        write_lf(tex_path, text)


def rewrite_index():
    """The problem-to-figures mapping, regenerated from the sources so it can't disagree with them."""
    index = {}
    for name in all_names():
        tex_path, svg_path = figure_paths(name)
        if not svg_path.exists():
            continue
        fig = Figure(name, tex_path.read_text(encoding="utf-8"))
        svg = svg_path.read_text(encoding="utf-8")
        index.setdefault(problem_id(name), []).append(dict(src=f"figures/{name}.svg?v={svg_version(svg)}", alt=fig.alt, after_paragraph=fig.after_paragraph))
    write_lf(INDEX, json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    return index


def build(names, check_only=False):
    failures = 0
    for name in names:
        tex_path, svg_path = figure_paths(name)
        if not tex_path.exists():
            print(f"{name}: no such figure", file=sys.stderr)
            failures += 1
            continue
        try:
            if not check_only:
                sync([name])
            built = build_source(name, tex_path.read_text(encoding="utf-8"))
        except FigureError as e:
            print(f"{name}: FAIL: {e}", file=sys.stderr)
            failures += 1
            continue
        for problem in built.layout:
            print(f"{name}: FAIL layout: {problem}", file=sys.stderr)
            failures += 1
        if check_only:
            if not svg_path.exists() or svg_path.read_text(encoding="utf-8") != built.svg:
                print(f"{name}: FAIL: the committed SVG differs from a fresh build", file=sys.stderr)
                failures += 1
        else:
            write_lf(svg_path, built.svg)
        print(f"{name}: {built.facts} facts held, {len(built.svg) // 1024} KB")
    if not check_only:
        rewrite_index()
    return failures


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m pipeline.figures")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("sync").add_argument("names", nargs="+")
    sub.add_parser("build").add_argument("names", nargs="*")
    sub.add_parser("check")
    add_arguments(sub.add_parser("attach"))
    args = ap.parse_args(argv)
    try:
        if args.command == "sync":
            sync(args.names)
            return 0
        if args.command == "attach":
            return run_attach(args)
        failures = build(getattr(args, "names", None) or all_names(), check_only=args.command == "check")
    except ToolchainError as e:
        print(f"Can't build figures on this machine: {e}", file=sys.stderr)
        return 3
    if failures:
        print(f"\n{failures} problem{'s' if failures > 1 else ''}.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
