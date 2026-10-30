# 10. Diagrams for geometry problems

## Goal
Let problems carry accurate, theme-aware figures, so the generator can write real geometry problems and the site can show them crisply in light and dark mode.

## Depends on
01, for the `figure` field in the schema.

## Spec
1. **Authoring format.** A figure is a small Python script, `figures/<id>.py`, using exact coordinates (sympy or plain floats computed from the problem's data). It writes `figures/<id>.svg`. Put a tiny helper library in `pipeline/figures/` with functions like `point`, `segment`, `circle`, `label`, `angle_mark` and `right_angle`.
2. **Theme awareness.** The SVG uses `currentColor` for strokes and labels and no hard-coded colours, so it inherits the page colour in both themes. Labels are in italic serif, to match the statement font.
3. **Accuracy check.** The script asserts the problem's given facts, such as tangency, lengths and concyclicity, at 1e-9 tolerance, so a figure can never contradict its statement. Not-to-scale figures are allowed only when the problem says so.
4. **Frontend.** The problem view shows `figure` inline after the statement, at a max width of 420 px, with a text alternative made from a `figure_alt` field.
5. **Pipeline hook.** The generator (06) can ask for a figure. The verification gate (05) runs the figure script and fails the draft if its assertions fail.
6. Add figures to the existing geometry seed problems as a demonstration.

## Acceptance criteria
- Five demo figures render correctly at desktop and phone widths in both themes, and have alt text.
- Deliberately breaking a figure, by moving a tangent point, makes its assertion fail.

## Out of scope
Interactive figures. Kevinvariant's Geometry Lab already does those, and a later task could link to it.
