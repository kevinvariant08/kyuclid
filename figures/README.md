# Solution figures

Each figure is real tkz-euclide: `<id>-solution[-n].tex` is the source, and `<id>-solution[-n].svg` is what the site inlines once a solution is unlocked. Visitors only load SVGs, so the site still has no build step.

```bash
python -m pipeline.figures build
```

Building needs MiKTeX or TeX Live with `tkz-euclide`, plus `dvisvgm`. Run `python -m pipeline.figures build <name>` for one figure. `build` fills in the decimals, checks every fact, compiles, checks the layout, writes the SVG and rewrites `index.json`.

## Rules for a source file

- Start from `\input{preamble}`, and draw only with its colours and styles (`aux`, `key`, `mk`, `lbl`, `len`, `figtint`, `figaccenttint`). Any other colour fails the build, because it wouldn't follow the theme.
- Every point is one line, `\tkzDefPoint(x,y){P} %! P = <exact value>`. `build` computes the decimals from the exact value. The exact value is evaluated at 50 digits.
- `%! fact` lines are checked to 1e-9, and the gate looks for any number after `==` in the statement or solution. `%! example` lines are checked the same way, but are for facts true only of the case drawn.
- `%! alt` is the text alternative, and `%! after_paragraph` says how many solution paragraphs come above the figure.
- Don't compute points in TeX with `\tkzDefMidPoint`, `\tkzInterLL`, `\tkzDrawCircle[circum]` and the like. The last one makes tkz-euclide 5 loop forever, so every compile has a 25-second limit.

Raw TikZ curves are the one gap. The radii of an ellipse or the formula of a parabola aren't tied to the exact values, so the facts can check points on the curve but not the curve itself. The figure critic and a human look at those.

## Theme and size

Strokes and labels use `currentColor`, and the accent uses `var(--fig-accent)`, set in `css/site.css` for each theme. An `<img>` SVG can't inherit these, so the problem view fetches the file and inlines it. Every figure is 1.6 px per point at full size, so labels and strokes match between figures. CSS only shrinks a figure to fit a phone. The build refuses anything over 270 by 300 pt, which keeps labels at 10.5 px or more on a 288 px column.

The service worker caches SVGs forever, so `src` carries `?v=<hash>`. `validate.mjs` fails a stale one.

## Attaching figures

`index.json` maps each problem ID to its figures, and is generated from the sources.

```bash
python -m pipeline.figures attach
```

That updates problems already in `data/problems`. To update review files as well, add `--dir review/pending --dir review/approved`. A review file then also holds its `.tex` and `.svg`, in the gate-only `figure_sources` field. Approving a draft in the review queue writes those files here, and also picks up any figures mapped to its ID in `index.json`.

## Which problems have figures

Every problem with topic G has one, and so has any other problem whose solution argues from a picture. Two non-G problems qualify:

- `three-chords`: the argument starts from chords of a parabola and their slopes.
- `colours-on-a-cut-up-decagon`: the induction removes a vertex from a triangulated polygon.

Every problem left out, with the reason. The rows for `a-product-of-two-sums` and the 16 others that weren't in the first pilot are drafts from the second generation batch, classified from their statements and tags:

| Problem | Topic | Why it has no figure |
|---|---|---|
| `sides-from-a-cubic` | A | "Triangle" only supplies three inequalities on the roots. |
| `black-cells-in-four-rows` | C | The 4-cycle is a bookkeeping graph, and the argument counts partitions of its edges. |
| `flipping-half-the-strings` | C | Vectors over the field with two elements, so there is nothing to draw in the plane. |
| `halfway-there` | C | Casework and binomial counting on a functional condition. |
| `the-fifteen-hundredth-term` | C | Counting strings by base representation. |
| `a-product-equal-to-one` | N | Valuations and parity. |
| `a-reshuffle-of-thirty-five` | N | A graph on pairs of residues, used for counting. The picture adds nothing to the argument. |
| `a-whole-total` | N | Multiplicative functions and prime factorisation. |
| `eight-divisors-of-thirty` | N | A recursion on exponent parities. |
| `first-whole-value` | N | Orders modulo n and telescoping. |
| `multiples-of-thirteen` | N | The roots of unity are only a product over the roots, and the argument works modulo 13. |
| `one-step-or-two` | N | "Jump points" are those of step functions, compared by algebra. |
| `remainders-of-a-growing-sum` | N | Completing the square and residues. "Triangular" only names the numbers. |
| `three-from-a-hundred` | N | A discriminant and bounds. |
| `three-matching-remainders` | N | "Coordinates" here means residues. |
| `three-units-of-digit-weight` | N | Residues and the rule of product. |
| `totals-never-reached` | N | Double counting and floor functions. |
| `a-product-of-two-sums` | A | Trigonometric identities, by algebra. |
| `one-coefficient-fixed` | A | A geometric series and a discriminant. |
| `repeats-in-a-family` | A | "Pencil" is only a name for a family of quadratics, handled by Vieta. |
| `settling-down` | A | A trigonometric substitution, used as algebra. |
| `the-first-missing-quotient` | A | Floor functions and bounds. |
| `words-and-a-weighted-tally` | A | A roots-of-unity filter, used as algebra. |
| `applied-twice` | C | Cycle decompositions of permutations. |
| `calm-words` | C | Counting words with stars and bars. |
| `eighteen-round-a-circle` | C | "Circle" means indices modulo 18. |
| `matching-ends` | C | A bijection on compositions. |
| `odd-meets-even` | C | Factorising and the rule of product. |
| `seven-cards-small-hand` | C | A recursion and a bijection on orderings. |
| `exactly-twenty-terms` | N | Digit sums and stars and bars. |
| `neighbours-trading-places` | N | Residues and place value. |
| `smallest-completions` | N | Multiplicativity and exponent parity. |
| `the-last-lonely-integer` | N | A linear Diophantine equation and bounds. |
| `three-primes-and-a-ratio` | N | Bounds on divisor functions. |
| `one-more-than-the-root` | N | Grouping a sum into blocks, with residues. |
