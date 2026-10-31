"""The figure tests. The first class needs nothing installed; the rest need TeX and say so when they skip.

    python -m unittest discover -s pipeline/figures/tests -t . -v
"""
import json
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from pipeline.figures import attach
from pipeline.figures.build import FIGURES, ToolchainError, _compile, _run, all_names, build_source, check_layout, figure_paths, preflight, svg_version, theme_svg
from pipeline.figures.source import Figure, FigureError, fact_numbers
from pipeline.verify import figure_check

TANGENT = r"""%! alt A circle with centre O touching line AB at T.
%! after_paragraph 1
%! scale 1/2
\input{preamble}
\begin{document}
\begin{tikzpicture}
\tkzDefPoint(0.000000,0.000000){O} %! O = (0, 0)
\tkzDefPoint(-3.000000,2.000000){A} %! A = (-6, 4)
\tkzDefPoint(3.000000,2.000000){B} %! B = (6, 4)
\tkzDefPoint(0.000000,2.000000){T} %! T = (0, 4)
%! fact tangent(O, 4, A, B)
%! fact on_circle(T, O, 4)
%! fact dist(A, B) == 12
\tkzDrawCircle(O,T)
\tkzDrawSegment(A,B)
\tkzDrawPoints(O,T)
\tkzLabelPoint[below,lbl](O){$O$}
\tkzLabelPoint[above,lbl](T){$T$}
\end{tikzpicture}
\end{document}
"""
MOVED_POINT = TANGENT.replace("%! T = (0, 4)", "%! T = (1, 4)").replace(r"\tkzDefPoint(0.000000,2.000000){T}", r"\tkzDefPoint(0.500000,2.000000){T}")
MOVED_LINE = TANGENT.replace("%! A = (-6, 4)", "%! A = (-6, 5)").replace("%! B = (6, 4)", "%! B = (6, 5)").replace("(-3.000000,2.000000)", "(-3.000000,2.500000)").replace("(3.000000,2.000000)", "(3.000000,2.500000)")

SOLUTION = "The line $AB$ has length $12$ and touches the circle.\n\nSo the answer is $7$."


def draft(tex, name="demo-solution", topic="G", svg=None):
    built = build_source(name, tex)
    return dict(id="demo", topic=topic, statement="A circle touches a line.", solution=SOLUTION, solution_figures=[dict(src=built.src, alt=built.alt, after_paragraph=built.after_paragraph)],
                figure_sources=[dict(name=name, tex=tex, svg=svg if svg is not None else built.svg)])


class WithoutTeX(unittest.TestCase):
    def test_every_committed_figure_holds_its_facts(self):
        names = all_names()
        self.assertGreaterEqual(len(names), 16)
        for name in names:
            with self.subTest(name):
                fig = Figure(name, figure_paths(name)[0].read_text(encoding="utf-8"))
                fig.check_decimals()
                self.assertGreater(fig.check_facts(), 0)
                self.assertTrue(fig.alt)

    def test_a_moved_tangent_point_fails_its_fact(self):
        fig = Figure("x", MOVED_POINT)
        with self.assertRaisesRegex(FigureError, "on_circle"):
            fig.check_facts()

    def test_a_moved_line_fails_tangency(self):
        with self.assertRaisesRegex(FigureError, "tangent"):
            Figure("x", MOVED_LINE).check_facts()

    def test_a_decimal_that_drifts_from_its_exact_value_fails(self):
        fig = Figure("x", TANGENT.replace(r"\tkzDefPoint(0.000000,2.000000){T}", r"\tkzDefPoint(0.100000,2.000000){T}"))
        with self.assertRaisesRegex(FigureError, "T is drawn at"):
            fig.check_decimals()

    def test_sync_fills_in_the_decimals(self):
        rough = TANGENT.replace("(-3.000000,2.000000)", "(0,0)")
        fig = Figure("x", Figure("x", rough).synced_tex())
        fig.check_decimals()

    def test_the_tolerance_is_tight(self):
        close = TANGENT.replace("%! T = (0, 4)", "%! T = (0, 4 + 1/100000000)")
        with self.assertRaisesRegex(FigureError, "on_circle"):
            Figure("x", close).check_facts()

    def test_dangerous_or_imprecise_tex_is_refused(self):
        for bad, why in [(r"\usepackage{xcolor}", "isn't allowed"), (r"\immediate\write18{calc}", "isn't allowed"), (r"\input{/etc/passwd}", "only .input"), (r"\def\x{1}", "isn't allowed"),
                         (r"\tkzDefMidPoint(A,B)", "computes in TeX"), (r"\tkzGetPoint{M}", "computes in TeX"), (r"\tkzDrawCircle[circum](O,A,B)", "computes in TeX"), (r"\tkzDefPoints{0/0/Z}", "exact value")]:
            with self.subTest(bad), self.assertRaisesRegex(FigureError, why):
                Figure("x", TANGENT.replace(r"\tkzDrawSegment(A,B)", bad))

    def test_expressions_cannot_reach_python(self):
        for bad in ["__import__('os')", "(1).real", "open('x')", "[1 for x in y]"]:
            with self.subTest(bad), self.assertRaises(FigureError):
                Figure("x", TANGENT.replace("%! T = (0, 4)", f"%! T = {bad}"))

    def test_a_point_needs_its_exact_value(self):
        with self.assertRaisesRegex(FigureError, "exact value"):
            Figure("x", TANGENT.replace("%! T = (0, 4)", ""))

    def test_theme_refuses_an_unknown_colour_and_prefixes_ids(self):
        raw = "<?xml version='1.0'?><svg width='10pt' height='10pt' viewBox='0 0 10 10'><g id='page1'><path id='a' d='M0 0L1 1' stroke='#000' fill='none'/><use xlink:href='#a'/></g></svg>"
        svg = theme_svg(raw, "fig")
        self.assertIn("id='fig-a'", svg)
        self.assertIn("href='#fig-a'", svg)
        self.assertIn("stroke='currentColor'", svg)
        self.assertNotIn("page1", svg)
        self.assertNotIn("10pt", svg)
        with self.assertRaisesRegex(FigureError, "colour #808080"):
            theme_svg(raw.replace("#000", "#808080"), "fig")
        with self.assertRaisesRegex(FigureError, "active"):
            theme_svg(raw.replace("<g id", "<script/><g id"), "fig")

    def test_layout_finds_overlapping_labels_and_lines_through_labels(self):
        glyph = "<path d='M{0} {1}H{2}V{3}H{0}Z'/>"
        head = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' fill='currentColor'>"
        one = glyph.format(10, 10, 16, 18)
        self.assertEqual(check_layout(head + one + glyph.format(50, 50, 56, 58) + "</svg>"), [])
        self.assertIn("overlap", " ".join(check_layout(head + one + glyph.format(12, 12, 18, 20) + "</svg>")))
        line = "<path d='M0 14L100 14' stroke='currentColor' fill='none'/>"
        self.assertIn("runs through", " ".join(check_layout(head + one + line + "</svg>")))
        self.assertIn("phone", " ".join(check_layout(head.replace("0 0 100 100", "0 0 400 100") + one + "</svg>")))

    def test_a_curve_written_with_the_smooth_command_is_followed(self):
        head = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' fill='currentColor'>"
        arc = "<path d='M0 50C0 20 20 0 50 0S100 20 100 50' stroke='currentColor' fill='none'/>"
        clear_of_the_chord = "<path d='M60 30H66V38H60Z'/>"
        self.assertEqual(check_layout(head + arc + clear_of_the_chord + "</svg>"), [])

    def test_a_process_that_hangs_is_killed_at_the_timeout(self):
        # tkz-euclide 5 spins forever on old syntax, as MiKTeX's pdflatex did here, so a compile must be stoppable.
        started = time.time()
        code, _ = _run([sys.executable, "-c", "import time; time.sleep(60)"], None, 1)
        self.assertIsNone(code)
        self.assertLess(time.time() - started, 30)

    def test_a_timeout_is_a_figure_failure_and_not_a_crash(self):
        with mock.patch("pipeline.figures.build._run", return_value=(None, "")), tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(FigureError, "still running"):
                _compile(Figure("x", TANGENT), d)

    def test_a_missing_tool_gets_one_plain_message(self):
        with mock.patch("pipeline.figures.build._preflight_ok", False), mock.patch("shutil.which", return_value=None):
            with self.assertRaisesRegex(ToolchainError, "pdflatex and dvisvgm not found"):
                preflight()

    def test_gate_only_asks_figures_of_pictures(self):
        self.assertTrue(figure_check.needs_figure(dict(topic="G", solution="x", statement="y")))
        self.assertFalse(figure_check.needs_figure(dict(topic="N", solution="Count residues.", statement="y")))
        self.assertTrue(figure_check.needs_figure(dict(topic="A", solution="In the complex plane the roots form a square.", statement="y")))
        self.assertFalse(figure_check.needs_figure(dict(topic="A", solution="In the complex plane...", statement="y", figure_exempt="Only algebra.")))
        status, reason, _ = figure_check.run(dict(topic="G", solution="x", statement="y"))
        self.assertEqual((status, "needs a figure" in reason), ("fail", True))

    def test_fact_numbers_are_the_plain_claims(self):
        self.assertEqual([n for _, n in fact_numbers(Figure("x", TANGENT))], ["12"])

    def test_attach_refuses_a_figure_past_the_end_of_an_edited_solution(self):
        fig = [dict(src="figures/x-solution.svg?v=00000000", alt="a", after_paragraph=3)]
        with self.assertRaisesRegex(ValueError, "now has 1"):
            attach.attach_to(dict(id="x", solution="One paragraph."), fig, carry_sources=False)

    def test_the_mapping_matches_the_files(self):
        index = json.loads((FIGURES / "index.json").read_text(encoding="utf-8"))
        names = sorted(f["src"].split("?")[0][len("figures/"):-4] for figs in index.values() for f in figs)
        self.assertEqual(names, all_names())
        for figs in index.values():
            for f in figs:
                svg = (FIGURES.parent / f["src"].split("?")[0]).read_text(encoding="utf-8")
                self.assertTrue(f["src"].endswith(svg_version(svg)))

    def test_no_private_id_in_public_figures(self):
        for p in FIGURES.iterdir():
            self.assertNotRegex(p.read_text(encoding="utf-8") if p.suffix != ".png" else "", r"AIME|AMC|inspired_by")


@unittest.skipUnless(shutil.which("pdflatex") and shutil.which("dvisvgm"), "TeX isn't installed, so compile tests are skipped")
class WithTeX(unittest.TestCase):
    def test_a_good_figure_passes_the_gate_check(self):
        status, reason, ev = figure_check.run(draft(TANGENT))
        self.assertEqual(status, "pass", reason)
        self.assertEqual(ev["figures"][0]["facts"], 3)

    def test_a_moved_tangent_point_fails_the_gate_check(self):
        d = draft(TANGENT)
        d["figure_sources"][0]["tex"] = MOVED_POINT
        status, reason, _ = figure_check.run(d)
        self.assertEqual(status, "fail")
        self.assertIn("on_circle", reason)

    def test_a_figure_that_does_not_compile_fails_the_gate_check(self):
        d = draft(TANGENT)
        d["figure_sources"][0]["tex"] = TANGENT.replace(r"\tkzDrawSegment(A,B)", r"\tkzDrawSegment(A,B")
        status, reason, _ = figure_check.run(d)
        self.assertEqual(status, "fail")
        self.assertIn("doesn't compile", reason)

    def test_a_number_the_text_never_mentions_fails(self):
        tex = TANGENT.replace("%! fact dist(A, B) == 12", "%! fact dist(A, O) == sqrt(52)\n%! fact dist(T, B) == 6")
        status, reason, _ = figure_check.run(draft(tex))
        self.assertEqual(status, "fail")
        self.assertIn("isn't in the statement or solution", reason)
        status, _, _ = figure_check.run(draft(tex.replace("%! fact dist(T, B) == 6", "%! example dist(T, B) == 6")))
        self.assertEqual(status, "pass")

    def test_a_stale_svg_fails(self):
        d = draft(TANGENT, svg="<svg></svg>")
        status, reason, _ = figure_check.run(d)
        self.assertEqual(status, "fail")
        self.assertIn("Rebuild", reason)

    def test_a_figure_past_the_why_line_fails(self):
        d = draft(TANGENT)
        d["solution"] = "One.\n\n<b>Why this works.</b> <code>x</code>: y."
        d["solution_figures"][0]["after_paragraph"] = 2
        status, reason, _ = figure_check.run(d)
        self.assertEqual(status, "fail")
        self.assertIn("after_paragraph", reason)

    def test_the_render_for_the_critic_is_written(self):
        with tempfile.TemporaryDirectory() as d:
            status, _, ev = figure_check.run(draft(TANGENT), d)
            self.assertEqual(status, "pass")
            self.assertGreater(Path(ev["renders"][0]).stat().st_size, 1000)

    def test_preflight_passes_here(self):
        preflight()

    def test_committed_svgs_match_a_fresh_build(self):
        for name in all_names():
            with self.subTest(name):
                tex, svg = figure_paths(name)
                built = build_source(name, tex.read_text(encoding="utf-8"))
                self.assertEqual(built.layout, [])
                self.assertEqual(built.svg, svg.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
