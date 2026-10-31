# 10. Diagrams for geometry problems

## Goal
Let problems carry accurate, theme-aware figures, so the generator can write real geometry problems and the site can show them crisply in light and dark mode.

## Depends on
01, for the `figure` field in the schema.

## Spec
Kevin chose tkz-euclide over the Python format first planned here. `figures/README.md` is the reference: format, build, attaching and the problems left out.

1. **Authoring format.** A figure is real tkz-euclide, `figures/<id>-solution[-n].tex`, built from exact coordinates over a shared preamble and compiled by MiKTeX to a committed SVG with `python -m pipeline.figures build`. The site has no build step.
2. **Theme awareness.** The SVG uses `currentColor` and `var(--fig-accent)`, and any other colour fails the build. The problem view inlines it, because an `<img>` can't inherit the page colour.
3. **Accuracy check.** Each `%! fact` is checked on the exact coordinates at 1e-9, and the decimals TeX draws with must match those coordinates.
4. **Frontend.** `solution_figures: [{src, alt, after_paragraph}]` appear inside the solution, once it is unlocked.
5. **Pipeline hook.** The generator must write a figure for any solution that argues from a picture. The gate compiles it, re-checks its facts and layout, and adds one Opus critic call that looks at a render. The review queue shows figures.
6. Figures for the live site's geometry problems and the pilot's geometry drafts, mapped by ID in `figures/index.json`.

## Acceptance criteria
- Every figure looked at on desktop and phone in both themes, with alt text.
- Breaking a figure, by moving a tangent point or by making it fail to compile, fails the gate.

## Out of scope
Interactive figures. Kevinvariant's Geometry Lab already does those, and a later task could link to it.
