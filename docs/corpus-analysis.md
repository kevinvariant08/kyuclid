# Corpus analysis

This covers wave 1 of task 03: the 1,035 AIME problems from 1983 to 2026. Every problem has an analysis record, kept privately in the corpus repository. No problem text appears here, only ids, slugs, counts and abstract descriptions.

**What generation should take from this:**
- Sample across the 119 idea families below, not in proportion to frequency. Three geometry families and some combinatorics ones are loose catch-alls, so treat their size with care.
- Treat kyu labels as good for ordering but possibly a notch easy. The two models disagree by a steady offset, described under [Kyu calibration](#kyu-calibration).
- AIME has almost no named olympiad geometry. Its geometry ladder stops short of what task 21 will need.

**Still open:**
- Kevin's review of 50 records, which needs at least 85% accepted.
- Kevin's approval of the 33 slugs in taxonomy 1.1.0. The records already use them, so rejecting one changes those records and the counts under Gaps.
- `AIME-2000-II-05`, whose record analyses a copied statement until task 02 restores the real problem.

The brief's other acceptance criteria are met for this wave.

## Method

| Stage | Model | Problems | Tokens | Agent time |
|---|---|---|---|---|
| First pass | Opus 5.5 | 1,011 | 6.24M | 8.5 h |
| Second pass, blind: all geometry plus a seeded 15% of the rest | Sonnet 5.5 | 411 | 2.82M | 2.7 h |
| Adjudication of disagreements | Opus 5.5 | 191 | 1.25M | 1.1 h |
| Idea families | Sonnet 5.5 | 1,034 | 0.39M | 0.2 h |

The other 24 problems keep their resolved pilot records, which had two passes already. The 7 pilot problems with statement figures were redone, because the pilot's analysts couldn't see figures. The full run's analysts could.

The run took about 19 weekly points of the plan, as an upper bound, since other sessions were running. No API money was spent. Before the run, the estimate was 9.6M tokens and 20–35 weekly points; the two passes took 9.1M.

A bug in the batch script dropped 31 second-pass problems and ran 39 twice. The 31 were then analysed separately, and the repeat became a same-model check, reported below.

**How disagreements were resolved.** A record went to an adjudicator if the topics differed, the technique sets had Jaccard below 0.5, or the configuration sets differed. Adjudicators read the problem and both readings, labelled at random, and decided what the mathematics supports. Kyu did not go to adjudication, for the reason under Kyu calibration.

## Agreement between the passes

| Measure | Opus against Sonnet (411) | Sonnet against itself (39) | Target |
|---|---|---|---|
| Topic differs | 4% | 3% | under 10% |
| Techniques differ (Jaccard below 0.5) | 23% | 8% | under 25% |
| Primary technique differs | 26% | 10% | information only |
| The pilot's stricter rule | 42% | 13% | information only |
| Mean Jaccard | 0.63 | 0.70 | |
| Configuration sets differ | 125 of 231 tagged | 6 of 16 tagged | |
| Configuration Jaccard below 0.5 | 68 of 231 | | |
| Kyu differs | 34% | 18% | |

Both targets are met, but the technique figure is close. Geometry alone is 25.6% and the other topics 16%. The sample is geometry-heavy, so weighting by the corpus gives about 19%. Technique disagreement is measured by set overlap because Kevin chose that after the pilot, when the stricter rule turned out to measure mostly run-to-run noise.

The full run changes one pilot conclusion. In the pilot, a model differed from its own earlier run at least as much as from the other model. Here the two models differ more than Sonnet differs from itself, so there is a real model effect. The repeat is only 39 problems, and both of its runs share a pack, so this is suggestive.

Of the 191 adjudicated records, 154 changed from the first pass: techniques on 135, configurations on 46, the core idea on 32 and the topic on 4. Adjudicators named a specific false claim or misapplied tag in 58 records, usually a tag no listed path uses. Configurations are the weakest field, though set equality is a harsh test of them. Records outside the second pass have one reading only, but all geometry had two.

## Topic and technique frequency

| Kyu | A | C | G | N | Total |
|---|---|---|---|---|---|
| 7 | 17 | 7 | 2 | 6 | 32 |
| 6 | 75 | 48 | 36 | 60 | 219 |
| 5 | 86 | 81 | 75 | 58 | 300 |
| 4 | 76 | 70 | 113 | 53 | 312 |
| 3 | 23 | 30 | 64 | 31 | 148 |
| 2 | 1 | 5 | 15 | 2 | 23 |

Geometry grows with difficulty: 15 of the 23 problems at 2 kyu. Every topic has at least 23 problems at each of 5, 4 and 3 kyu, which is enough for task 06's cells.

**Over time:**

| Years | Problems | A | C | G | N | Mean kyu |
|---|---|---|---|---|---|---|
| 1983–1989 | 105 | 34% | 16% | 26% | 24% | 5.39 |
| 1990–1999 | 150 | 28% | 23% | 29% | 20% | 5.19 |
| 2000–2009 | 299 | 28% | 21% | 32% | 20% | 4.57 |
| 2010–2019 | 300 | 25% | 27% | 29% | 19% | 4.38 |
| 2020–2026 | 180 | 23% | 26% | 30% | 22% | 4.18 |

Algebra's share has fallen by a third and combinatorics has risen. The fall in mean kyu at 2000 is partly built in, because classic papers start one kyu easier by rule. The fall within the modern years is not.

The share of problems using a technique, 1983–1999 against 2010–2026:
- **Rising:** `casework` (6% to 20%), `modular-arithmetic` (5% to 11%), `coordinate-bash` (6% to 10%), `similar-triangles` (6% to 10%), `rule-of-product` (5% to 8%), `inscribed-angle-theorem` (1% to 4%), `symmetry-reduction` (5% to 8%), `crt` (2% to 5%), `place-value-representation` (1% to 4%), `power-of-a-point` (1% to 4%).
- **Falling:** `difference-of-squares` (7% to 2%), `factor-pair-enumeration` (5% to 1%), `binomial-theorem` (5% to 1%), `linear-system-solving` (7% to 4%), `angle-sum-formula` (5% to 2%), `area-by-decomposition` (7% to 4%), `arithmetic-series-sum` (6% to 3%), `bounding` (15% to 12%), `pairing-terms` (5% to 2%), `geometric-interpretation` (3% to 1%).

**Most used at each kyu:**
- **7 kyu:** `complementary-counting`, `linear-system-solving`, `bounding`, `linear-combination-of-equations`, `polynomial-factoring`, `rule-of-product`, `binomial-selection`.
- **6 kyu:** `linear-system-solving`, `casework`, `bounding`, `prime-factorization`, `log-properties`, `arithmetic-series-sum`, `binomial-selection`, `pythagorean-theorem`.
- **5 kyu:** `casework`, `bounding`, `similar-triangles`, `symmetry-reduction`, `coordinate-bash`, `rule-of-product`, `recursion`, `binomial-selection`.
- **4 kyu:** `casework`, `bounding`, `pythagorean-theorem`, `coordinate-bash`, `similar-triangles`, `recursion`, `law-of-cosines`, `modular-arithmetic`.
- **3 kyu:** `casework`, `bounding`, `coordinate-bash`, `law-of-cosines`, `similar-triangles`, `modular-arithmetic`, `pythagorean-theorem`, `double-and-half-angle-formulas`.
- **2 kyu:** `angle-chasing`, `inscribed-angle-theorem`, `law-of-cosines`, `law-of-sines`, `casework`, `bounding`, `inradius`, `reflection-across-line`.

**The technique the crux turns on, by topic:**
- **A:** `log-properties` (22), `rate-and-mixture-modeling` (19), `polynomial-factoring` (16), `linear-combination-of-equations` (13), `floor-function` (12), `vieta` (12).
- **C:** `casework` (39), `recursion` (24), `bijection` (15), `inclusion-exclusion` (12), `complementary-counting` (10).
- **G:** `similar-triangles` (53), `pythagorean-theorem` (20), `angle-chasing` (19), `area-ratios` (13), `reflection-across-line` (13).
- **N:** `modular-arithmetic` (22), `bounding` (20), `coprime-divisibility` (13), `p-adic-valuation` (11), `factor-pair-enumeration` (11), `divisor-counting` (11).

## What separates adjacent kyus

| Kyu | Steps in a collected path | Techniques | Paths | Long | High computation | High generation potential | Reason mentions a hidden step |
|---|---|---|---|---|---|---|---|
| 7 | 3.1 | 2.9 | 2.2 | 0% | 0% | 6% | 25% |
| 6 | 3.5 | 3.1 | 2.3 | 0% | 0% | 11% | 22% |
| 5 | 3.8 | 3.7 | 2.6 | 0% | 0% | 47% | 19% |
| 4 | 4.1 | 4.1 | 2.6 | 1% | 0% | 71% | 30% |
| 3 | 4.4 | 4.4 | 2.6 | 17% | 1% | 70% | 52% |
| 2 | 5.2 | 4.6 | 2.4 | 61% | 13% | 30% | 87% |

The last column is a keyword search of the analysts' kyu reasons, so it is a rough signal. Kyu is also tied to paper position by the one-step rule, so these are differences within what position already implies, and they are not independent evidence of difficulty.

In concrete terms:
- **6 to 5:** more techniques in play (3.1 to 3.7), and the idea starts to transplant. Problems at 6–7 kyu are often too plain to vary, at 6–11% high generation potential, against 47% at 5 kyu.
- **5 to 4:** a little more length and a second idea that has to combine with the first. No single count separates these well, and they are the hardest pair to tell apart.
- **4 to 3:** the crux becomes hidden. Hidden-step language jumps from 30% to 52%, and long solutions appear.
- **3 to 2:** length dominates as well as insight: 61% are long, and hidden-step language reaches 87%. Fewer of these ideas transplant, at 30% high potential, because more depend on a particular setting.

The number of viable paths does **not** separate kyus. It stays at 2.2–2.6 throughout, and the share with only one path shows no trend. Harder problems don't have fewer routes, at least among routes the analysts could find. Computation load barely separates them either, as analysts rated it high on only 13% even at 2 kyu.

## Kyu calibration

Kyu starts from paper position, one kyu easier in classic papers, and moves at most one step.

| Era | Position | Problems | 7 | 6 | 5 | 4 | 3 | 2 | Mean | Second pass mean |
|---|---|---|---|---|---|---|---|---|---|---|
| Modern | 1–5 | 259 | | 147 | 110 | 2 | | | 5.56 | 5.12 |
| Modern | 6–10 | 260 | | | 99 | 155 | 6 | | 4.36 | 4.05 |
| Modern | 11–15 | 260 | | | | 102 | 135 | 23 | 3.30 | 2.95 |
| Classic | 1–5 | 85 | 32 | 51 | 2 | | | | 6.35 | 6.10 |
| Classic | 6–10 | 85 | | 21 | 64 | | | | 5.25 | 5.03 |
| Classic | 11–15 | 85 | | | 25 | 53 | 7 | | 4.21 | 3.95 |

The second-pass mean covers only double-passed problems, whose first-pass means are slightly lower than the table's.

**The kyu difference is a rater effect.** Where the passes differ on kyu, Sonnet is the harder one 123 times and the easier one 16 times. Opus moved about 35% of the shared problems one kyu easier, and Sonnet moved 12%. So the first pass's picture of modern AIME spanning 6 to 2 kyu, with most of positions 1–5 at 6 kyu, is not something the second rater reproduces. Under Sonnet those positions sit near 5 kyu, as the brief's table has them. Neither rater is shown to be right: the corpus has no outside difficulty data, since the AIME source gives no MOHS or vote figures.

**The rule applied.** All records keep the first pass's kyu, and the second pass's is kept alongside it where one exists. Geometry was double-passed and most other problems were not, so resolving kyu record by record would have made geometry look harder purely because of the method. The cost is that labels may run about a third of a kyu easy across the board. A recalibration against real solver data, or against wave 2's contests, should fix this properly.

## Idea families

The 1,034 usable problems fall into 119 families, with a median size of 7 and a largest of 26. A family is a set of problems a strong solver would recognise as one idea in different clothes. Sonnet grouped them by topic, from `core_idea` and `crux`, and no second pass checked the grouping. The private records carry each problem's family.

These are loose, and they collect what fit nowhere more specific, so their size says little about the corpus: `law-of-sines-and-cosines-with-angle-chains`, `right-triangle-pythagorean-bookkeeping`, `coordinate-description-of-regions-and-centres`, `extremal-bound-with-matching-construction` and `inclusion-exclusion-over-forbidden-patterns`.

| Topic | Family | Size | Kyu | Idea |
|---|---|---|---|---|
| A | clever-polynomial-factoring-by-grouping | 17 | 7–3 | Recognise a hidden factorisation of a sparse, patterned or parametrised polynomial and read roots, counts or common factors from the factors. |
| A | symmetric-system-by-adding-or-multiplying-equations | 16 | 7–3 | Combine all equations of a symmetric or cyclic system by adding, subtracting or multiplying them so that a shared aggregate becomes the single unknown. |
| A | vieta-on-shifted-or-related-roots | 15 | 7–4 | Express a target through the elementary symmetric functions of a polynomial's roots, using how the needed roots relate to the given ones, and read the answer from coefficients. |
| A | log-system-to-linear-in-logs | 14 | 7–4 | Rewrite several logarithmic relations in a common base so that they become a linear or reciprocal-sum system in the logarithms of the unknowns, and solve for a symmetric target. |
| A | equal-time-motion-and-work-rates | 13 | 6–5 | Model agents with constant rates or speed ratios, and equate times or distances across scenarios to get a linear or quadratic relation in the unknown rate. |
| A | log-equation-to-quadratic-in-a-log | 12 | 6–3 | Take logarithms of an equation with the unknown in base and exponent, or unwind nested logarithms, so it becomes a polynomial in one logarithm whose roots give the requested product or value. |
| A | unit-circle-powers-de-moivre | 12 | 6–3 | Place unknowns on the unit circle, write them in polar form, and let powers multiply the angle so conditions become congruences or geometric sums. |
| A | proportion-and-percent-change-linear-relation | 10 | 6–4 | Translate ratios, percentages or conserved totals across a before-and-after comparison into one linear equation in the unknown quantity. |
| A | difference-of-squares-and-pairing-terms | 10 | 7–4 | Group terms of an alternating sum or product into pairs so differences of squares or common factors collapse it to an arithmetic sum. |
| A | finite-order-map-or-recurrence-periodicity | 9 | 6–4 | An iterated map or recurrence returns to its start after a few steps, so a huge iterate reduces to a small one. |
| A | arithmetic-progression-parametrization | 9 | 7–5 | Parametrise a progression by its centre and common difference so sums, means and extreme terms follow from a few linear conditions. |
| A | mean-inequality-optimization | 9 | 6–3 | Bound an expression with a mean or Cauchy-type inequality or by completing a square, then check that equality is attainable. |
| A | power-sums-from-sum-and-product | 8 | 7–3 | Rewrite power sums or symmetric conditions of a few unknowns via their sum and product, then use a recurrence or elimination to reach the target. |
| A | floor-function-value-structure | 8 | 5–3 | Use monotonicity, jumps or periodic shifts of an expression containing integer parts to find which values are attained or where the sum reaches a target. |
| A | roots-of-unity-sums-and-products | 8 | 6–3 | Use symmetry of equally spaced roots of unity to evaluate sums, chord-length products or resultants over all roots. |
| A | geometric-progression-ratio-elimination | 8 | 6–4 | Divide or compare conditions on geometric progressions, or perturb them into arithmetic ones, to eliminate the first term and solve for the ratio. |
| A | mean-change-gives-count-and-total | 7 | 7–4 | A known change in an average on adding or removing items pins down the count and total, giving a small linear system or inequality. |
| A | floor-of-log-or-root-constant-on-blocks | 7 | 7–3 | A floor, ceiling or rounding of a logarithm or root is constant on predictable blocks, so sums and counts are done block by block. |
| A | tangent-addition-merging | 7 | 7–3 | Combine inverse tangents or cotangents, or tangent sums, step by step with the addition formula to reach a simple closed value. |
| A | trig-identity-ratio-system | 7 | 6–3 | From given ratios or sums of trigonometric functions, use Pythagorean, double-angle or sum-to-product identities to solve for the requested value. |
| A | hidden-perfect-power-binomial | 7 | 6–5 | A polynomial or expression is a binomial expansion in disguise after shifting or completing, collapsing it to a pure power equation or a few leading terms. |
| A | recurrence-linearised-by-substitution | 7 | 5–3 | A nonlinear recurrence or nested fractional expression becomes linear or arithmetic after a substitution, or has a conserved quantity or fixed-point structure. |
| A | algebraic-telescoping-sum | 6 | 5–2 | Split a summand by partial fractions or logarithms so consecutive terms cancel and the sum collapses to boundary terms. |
| A | distance-and-path-geometric-interpretation | 6 | 7–3 | Read sums of absolute values or radicals as distances or path lengths, so optimisation or area follows from geometry. |
| A | polynomial-composition-root-structure | 6 | 6–3 | Use finiteness of roots or fibre structure of a composed or functionally defined polynomial to determine its roots and degree. |
| A | function-symmetries-compose-to-translation | 5 | 5–4 | Several reflection or scaling symmetries of a function compose to a translation or similarity, forcing periodic or self-similar structure and counting forced zeros. |
| A | trig-telescoping-by-multiplying-a-sine | 5 | 4–3 | Multiply a trigonometric sum or product by a well-chosen sine or cotangent so product-to-sum identities make it collapse. |
| A | complex-rotation-and-affine-iteration | 5 | 5–4 | Model a construction as repeated rotation and scaling in the complex plane and find a vertex, limit or fixed point by solving a linear equation. |
| A | conjugate-pairs-of-nonreal-roots | 5 | 6–4 | A real polynomial's nonreal roots come in conjugate pairs, so a known nonreal root brings a quadratic factor and constrains coefficients or counts. |
| A | integer-count-or-budget-diophantine | 5 | 6–4 | Reduce a problem to integer unknowns such as counts under a linear constraint, then optimise or enumerate the integer solutions. |
| A | equate-real-and-imaginary-parts | 4 | 6–5 | Impose a realness or pure-imaginary condition on a complex expression and split into two real equations in the coordinates. |
| A | reduce-powers-modulo-a-polynomial | 4 | 5–4 | Reduce high powers of roots modulo their minimal polynomial so a sum or integrality condition involves only low powers. |
| A | graph-crossing-count-of-folded-functions | 4 | 5–3 | Count solutions as crossings of graphs by restricting the domain and counting crossings per period or monotone piece. |
| A | rational-equation-substitution-on-repeated-block | 3 | 6–3 | A rational or homogeneous equation repeats a common block, so naming the block or the ratio of variables reduces it to a low-degree equation in one new variable. |
| C | extremal-bound-with-matching-construction | 16 | 6–2 | Find the maximum or minimum size of a structure by proving a counting bound and exhibiting a greedy or explicit construction that attains it. |
| C | inclusion-exclusion-over-forbidden-patterns | 12 | 7–4 | Count objects avoiding several overlapping bad events by complement and inclusion-exclusion, with overlap sizes determined by how the events interact. |
| C | multiset-arrangement-and-table-casework | 12 | 5–4 | Count fillings of a table or arrangements of a multiset under row and column constraints by casework on a small governing parameter. |
| C | gap-placement-for-non-adjacent-selection | 11 | 5–2 | Count selections or arrangements with adjacency restrictions by placing the unrestricted items first and choosing gaps, or by shifting positions to remove forced spacing. |
| C | markov-state-reduction-for-walks | 11 | 6–3 | Track a random walk or process by merging equivalent states under symmetry so that a short recurrence or linear system remains. |
| C | symmetric-point-configuration-counting-by-type | 10 | 7–2 | Count shapes formed by points of a symmetric configuration by classifying them into a few congruence or position types and counting each type once. |
| C | probability-by-pair-symmetry-and-counting | 10 | 6–5 | Find the chance for a random pair or position by counting favourable pairs directly, using swap symmetry or position-dependent window counts. |
| C | run-and-block-composition-counting | 9 | 5–3 | Count words or paths by decomposing them into maximal runs or blocks, so the count becomes a count of compositions with local size conditions. |
| C | staged-process-sequential-conditioning | 9 | 6–4 | Compute the chance of success in a multi-stage random process by conditioning stage by stage on what remains or on the unknown opponent. |
| C | digit-string-counting-with-positional-constraints | 9 | 7–5 | Count numerals or strings with constraints on particular positions by fixing the most constrained places first and multiplying the free choices. |
| C | independent-trial-comparison-symmetry | 8 | 6–4 | Compare or equate probabilities of independent trial outcomes by cancelling common coefficients or using the symmetry between complementary outcomes. |
| C | power-set-sum-and-complement | 8 | 7–3 | Count subsets with size or sign conditions as the full power set minus excluded classes, or by pairing subsets to cancel terms. |
| C | residue-class-structure | 8 | 5–3 | Use residues, parity or periodicity to force a rigid structure on a configuration, so that the count reduces to choices per class. |
| C | functional-graph-and-cycle-structure | 7 | 5–2 | Count maps or permutations with an iteration condition by describing them as graphs of cycles and trees and enumerating the allowed shapes. |
| C | waiting-time-and-first-event-recurrence | 7 | 5–3 | Find which event occurs first or when a pattern completes by conditioning on the current state or round, giving a linear system, recurrence or geometric sum. |
| C | unordered-correction-by-symmetric-division | 7 | 6–4 | Count ordered configurations first, remove the degenerate ones fixed by the swap, and divide by the symmetry to count unordered ones. |
| C | binomial-coefficient-identity-evaluation | 7 | 6–3 | Collapse a sum or ratio of binomial coefficients into a single term by reflection, factoring or a convolution identity. |
| C | local-transition-rule-recurrence | 6 | 6–4 | Count sequences governed by a local successor rule by building them one step at a time, with a uniform number of continuations or a short recurrence. |
| C | conditional-probability-from-overlap-data | 6 | 6–4 | Recover a target probability from given marginal and conditional information by writing the outcome space as atoms and solving for the unknown one. |
| C | carry-and-increment-analysis | 6 | 7–4 | Analyse positional addition or incrementing by where carries occur, so that interactions between places reduce to a small number of cases. |
| C | extreme-element-over-all-subsets | 6 | 6–3 | Total or average an extreme value over all subsets of a given size by counting, for each element, the subsets in which it is extreme. |
| C | process-periodicity-and-elimination | 6 | 6–3 | Understand a deterministic process by computing small cases or self-similarity, revealing a period or a smaller copy of the same process. |
| C | lattice-grid-geometry-counting | 6 | 6–4 | Count lattice points, cells or axis-parallel shapes in a grid region by translating geometry into selections of lines or points. |
| C | double-counting-incidences-and-totals | 5 | 6–3 | Count a conserved total in two ways, by element and by group, to obtain an equation that fixes an unknown quantity. |
| C | tournament-orientation-degree-structure | 5 | 5–3 | Analyse orientations of a complete graph through out-degree conditions, which force uniqueness or a transitive structure and lead to inclusion-exclusion or a bijection. |
| C | lattice-path-ballot-counting | 5 | 5–4 | Count monotone paths or staircase states under a boundary condition by encoding them as words and applying a ballot or reflection count. |
| C | insertion-of-extreme-element-recursion | 4 | 6–3 | Count arrangements under a local inequality by inserting the extreme element into a valid smaller arrangement, where its number of legal slots does not depend on the rest. |
| C | geometric-probability-region-area | 4 | 6–4 | Model independent continuous choices as a point in a product space and find the probability as an area of a simple region or its complement. |
| C | regions-from-crossings | 4 | 6–3 | Count the pieces cut by chords or lines in general position as a constant plus lines plus crossings, and count crossings combinatorially. |
| C | rotation-orbit-counting | 4 | 6–3 | Count objects up to rotation or shift by separating those with extra symmetry and determining the structure through orbit sizes. |
| C | base-expansion-encoding | 4 | 5–4 | Use uniqueness of base representation to turn a counting or position question into a statement about digit strings. |
| C | linear-equation-solution-counting | 4 | 6–4 | Count solutions of a linear condition by finding the possible count vectors and weighting them, or by substitution to a standard separator count. |
| C | polyhedron-incidence-counting | 3 | 6–5 | Count vertices, edges and pairs of a solid from local incidence data without picturing it, and take the remainder as the requested class. |
| C | multinomial-from-forced-internal-order | 2 | 6–5 | When each group has a forced internal order or independent cut points, the count factors into a multinomial arrangement of group labels times an independent count of divisions. |
| G | law-of-sines-and-cosines-with-angle-chains | 26 | 6–3 | Equal segments or angle conditions create isosceles triangles and angle chains, and a law of sines or cosines relation in one variable pins down the length or angle. |
| G | parallel-lines-forming-similar-copies-in-a-triangle | 23 | 6–4 | Lines parallel to the sides cut off similar copies of a triangle, so linear ratios add or scale and areas follow from the similarity ratio. |
| G | tangent-circles-and-common-tangents-by-centre-geometry | 23 | 6–2 | Mutually tangent circles are replaced by their centres, whose distances are sums or differences of radii, giving right triangles, collinearity or linear interpolation toward a common tangent. |
| G | incircle-tangent-lengths-and-semiperimeter | 21 | 6–2 | Tangent segments from vertices to an inscribed circle are expressed through side lengths and the semiperimeter, and combined with area or angle relations. |
| G | power-of-a-point-and-chords-through-a-point | 20 | 6–2 | Chord and secant lengths through a point are related by equal products or by right triangles from the centre to chord midpoints, and radical axes link several circles. |
| G | right-triangle-pythagorean-bookkeeping | 19 | 6–3 | The answer comes from locating a right triangle in the figure and chaining Pythagorean or similarity relations through a short computation. |
| G | cevian-area-ratios-and-mass-points | 18 | 6–3 | Segment ratios along cevians are converted into area ratios of sub-triangles, which are then summed or compared to solve for the unknown ratio or area. |
| G | plane-section-and-dissection-of-solids | 15 | 6–3 | A volume or surface is found by completing, dissecting or comparing a solid with a cut or similar sub-solid. |
| G | dihedral-angle-and-pyramid-height | 13 | 6–3 | The height of a pyramid-like solid comes from a right triangle in a symmetry section or from converting a dihedral angle into a planar angle. |
| G | cyclic-quadrilateral-and-ptolemy-relations | 12 | 6–2 | Chords and diagonals of a cyclic polygon satisfy product relations or angle relations that turn equal arcs or chords into a closed system of lengths. |
| G | round-bodies-reduced-to-a-planar-section | 10 | 6–4 | Tangent or contained round solids are handled by passing a plane through their centres, so the question becomes a planar tangency or distance problem. |
| G | arc-midpoint-and-bisector-circumcircle-lemmas | 10 | 4–2 | Angle bisectors, arc midpoints, symmedians and tangents at the circumcircle give standard lemmas that fix lengths or angles in a triangle with its circumcircle. |
| G | concyclicity-and-similar-triangles-by-angle-transfer | 10 | 5–3 | Equal angles are transferred through circles and shared points to expose concyclic points or similar triangles, from which a length ratio follows. |
| G | reflection-or-folding-to-fix-an-axis-or-shortest-path | 10 | 5–2 | A reflection or fold is used through its perpendicular bisector axis, or to straighten a broken path into a minimal one. |
| G | rotation-to-gather-lengths-or-compose-motions | 9 | 5–3 | A rotation about a point or composition of rotations carries pieces of a figure together, giving a congruent or equilateral triangle that fixes a length. |
| G | extremal-position-and-bounding-arguments | 9 | 4–3 | An optimum or tight configuration is found by pushing a figure into an extreme position or by matching two opposite bounds. |
| G | coordinate-description-of-regions-and-centres | 9 | 6–3 | Coordinates, signed distances or a linear map describe a point, centre or region directly, and an area or condition follows by computation. |
| G | regular-and-equiangular-polygon-structure | 8 | 6–3 | The structure of a regular or equiangular polygon gives angle or side relations that determine a length, area or count. |
| G | solid-embedded-in-box-or-scaled-dual | 7 | 6–3 | A symmetric solid is understood by embedding it in a simpler enclosing solid or by relating it to its scaled dual, so lengths and volumes follow from one linear factor. |
| G | unfolding-a-path-or-surface-into-a-line | 7 | 6–3 | A path, reflection sequence or rolling motion is straightened by unfolding or developing the surface, turning it into a straight segment or an arc-length equality. |
| G | mutually-perpendicular-edges-at-a-corner | 6 | 7–3 | Mutually perpendicular edges at a vertex supply orthogonal directions whose squared components or projections give a distance, normal or radius. |
| G | complex-numbers-and-loci-as-planar-geometry | 6 | 5–3 | A complex-number or modulus condition is read as a circle, bisector, conic or other locus whose geometry decides the answer. |
| G | central-symmetry-and-lines-through-the-centre | 5 | 7–3 | A line through the centre of a centrally symmetric figure bisects it, so balance conditions locate the centre or fix a line. |
| G | self-similar-chains-and-geometric-series | 5 | 6–3 | A chain of inscribed or shrinking figures shares a constant similarity ratio, so sizes or areas form a geometric progression or series. |
| G | geometric-probability-as-area-of-region | 4 | 6–4 | A probability over a continuous region is the area of the admissible set cut out by lines or perpendicular bisectors. |
| N | divisor-count-from-prime-exponents | 20 | 7–3 | Translate a condition on divisors into a condition on the exponent pattern of the prime factorisation and count or optimise over the admissible patterns. |
| N | crt-independent-moduli-counting | 18 | 7–3 | Split conditions across coprime moduli, solve or count each independently, and recombine by the Chinese remainder theorem. |
| N | shifted-factoring-of-bilinear-equations | 14 | 6–4 | Add a constant to a bilinear Diophantine relation so it factors, then enumerate factor pairs of a known integer. |
| N | perfect-square-via-difference-of-squares | 14 | 6–3 | Force an expression to be a perfect square by trapping it between squares or writing it as a difference of squares equal to a constant, then list factor pairs. |
| N | valuation-counting-and-factorial-multiples | 13 | 6–2 | Compute or compare prime exponents by counting multiples of prime powers, then use the resulting floor counts to decide the question. |
| N | place-value-divisibility-conditions | 13 | 7–3 | Write a number in place-value form and convert a divisibility or ratio condition into constraints among its digits. |
| N | linear-integer-forms-and-attainable-values | 10 | 6–3 | Study which values an integer linear form attains, using exchange moves, residue classes and size bounds on the unknowns. |
| N | finite-search-by-size-bounds | 9 | 6–3 | Use growth or positivity to bound unknowns so that only a short explicit list of cases remains to be checked. |
| N | prime-wise-lcm-gcd-reasoning | 8 | 7–4 | Least common multiples and greatest common divisors act as maximum and minimum on prime exponents, so conditions split into independent exponent constraints. |
| N | numerals-in-several-bases-linear-equation | 8 | 6–4 | A value written in different bases, or with shared digits across bases, gives a linear equation in the digits bounded by digit ranges. |
| N | multiplicative-order-confines-exponent | 7 | 5–3 | Divisibility of a difference of powers by a coprime modulus holds exactly when the exponent gap is a multiple of the multiplicative order, which restricts exponents or primes. |
| N | reduced-fractions-and-coprime-residue-counts | 7 | 6–3 | Count reduced fractions or coprime residues using totients, symmetry and inclusion-exclusion over the prime factors of the denominator. |
| N | periodicity-of-sequences-and-sums | 7 | 7–3 | A sequence or running sum over a finite state space repeats, so a far-off term reduces to a small index. |
| N | interval-between-consecutive-powers | 7 | 5–3 | Fit a condition between consecutive perfect powers or floor boundaries, and count by comparing gap length with block length. |
| N | base-expansion-correspondence | 6 | 6–4 | Identify a sequence or set with the digits of an index in some base, including signed digits, and read off the answer by reinterpreting digits. |
| N | binomial-expansion-for-power-congruences | 5 | 6–3 | Expand a power of a number near a multiple of the modulus so that only the first few terms survive the reduction. |
| N | divisor-pairing-around-the-square-root | 5 | 6–3 | Pair each divisor with its cofactor so that products, sums or counts over divisors collapse to a statement about the square root. |
| N | digit-sum-and-carry-tracking | 5 | 6–3 | Track how carries change a digit sum, or use digit-sum congruences, to constrain or optimise a number. |
| N | digit-permutation-and-reversal | 5 | 6–4 | Compare a number with a rearrangement or reversal of its digits, so that the difference or sum depends only on a few place values. |
| N | integer-progressions-with-rational-ratio | 5 | 6–3 | Parametrise arithmetic or geometric progressions with integer terms and use integrality to restrict the common difference or ratio. |
| N | geometric-setting-to-integer-condition | 5 | 6–2 | Translate a geometric or combinatorial setup into a number-theoretic condition on integer parameters. |
| N | squareful-values-via-exponent-parity | 4 | 6–5 | A quantity is a perfect square exactly when every prime exponent is even, so count or constrain by the squarefree part. |
| N | consecutive-run-sum-factorisation | 4 | 6–5 | A sum of consecutive integers is a product of its length and a mean, so representations correspond to factor pairs of the doubled total with matching parity. |
| N | prime-power-allocation-between-coprime-factors | 4 | 5–4 | When coprime factors multiply to something divisible by a prime power, the whole prime power must lie in one factor, giving a small list of cases. |
| N | polynomial-values-divisibility | 4 | 7–4 | Reduce divisibility questions about polynomial values by substituting a root, taking differences or eliminating the variable. |
| N | multiplicative-sums-factorise-per-prime | 3 | 5–3 | A sum over divisors with a multiplicative structure factorises as a product of independent geometric sums, one for each prime. |

## Gaps

219 techniques are active and 58 configurations are listed, beyond the brief's rough 200, because the run added 33 slugs. Each addition was asked for by at least two records after synonyms were merged. They are marked `run-proposed` in `data/taxonomy.json` as version 1.1.0, and Kevin hasn't reviewed them yet.

**Not used at all, so AIME can't teach generation anything about them:** `cauchy-fe`, `tangent-line-trick`, `vieta-jumping`, `chevalley-warning`, `derangements`, `wilson-theorem`, `zsigmondy`. Most were seeded for the olympiad wave.

**Used one to three times, so generation should take care, or look to wave 2:**
- **A:** `cauchy-schwarz`, `descartes-rule-of-signs`, `holder`, `inverse-function-analysis`, `jensen`, `lagrange-interpolation`, `palindromic-polynomial-reduction`, `pencil-of-curves`, `polynomial-root-transformation`, `rearrangement`, `remainder-factor-theorem`, `smoothing`, `sos`, `trig-substitution`.
- **C:** `catalan-paths`, `colouring-argument`, `eulerian-trail`, `extremal-principle`, `invariant`, `markov-states-expected-value`, `monovariant`, `pascal-weights`, `regions-from-crossings`, `weighted-binomial-sum`.
- **G:** `affine-stretch-to-circle`, `ceva`, `complex-bash`, `direction-cosines`, `euler-polyhedron-formula`, `harmonic-bundles`, `picks-theorem`, `spiral-similarity`, `trig-ceva`.
- **N:** `euclidean-algorithm`, `lte`, `pell-equation`, `quadratic-residues`.

Some of the 33 additions are in this range too, as expected of niche tools.

`invariant`, `monovariant`, `extremal-principle` and `quadratic-residues` being this rare is the clearest sign of what an answer contest leaves out. They belong to olympiad problems, so tasks 08 and 09 shouldn't calibrate them from AIME.

**Generation potential**, as rated by the first pass:

| Topic | High | Medium | Low |
|---|---|---|---|
| A | 119 | 121 | 38 |
| C | 123 | 98 | 20 |
| G | 151 | 140 | 14 |
| N | 106 | 91 | 13 |

Algebra has the most problems too tied to their setting to reuse.

## Geometry deep-dive

305 problems are geometry, 216 of them with a configuration tagged, and the figure is necessary for 18. These are the most common configurations at each kyu, with counts:

| Kyu | Problems | Configurations |
|---|---|---|
| 7 | 2 | none tagged |
| 6 | 36 | `mutually-tangent-circles` (6), `perpendicular-from-center-to-chord` (4), `parallel-segments-in-triangle` (4), `special-right-triangles` (3) |
| 5 | 75 | `parallel-segments-in-triangle` (12), `isosceles-triangle-axis` (10), `special-right-triangles` (6), `two-tangents-from-a-point` (5), `angle-in-semicircle` (4), `right-triangle-altitude` (4), `isosceles-trapezoid` (4) |
| 4 | 113 | `cyclic-quadrilateral` (11), `perpendicular-from-center-to-chord` (10), `mutually-tangent-circles` (10), `isosceles-triangle-axis` (10), `parallel-segments-in-triangle` (8), `right-triangle-altitude` (7), `two-tangents-from-a-point` (7), `isosceles-trapezoid` (7) |
| 3 | 64 | `cyclic-quadrilateral` (11), `two-intersecting-circles` (7), `isosceles-triangle-axis` (6), `two-tangents-from-a-point` (6), `angle-in-semicircle` (5), `incircle-and-semiperimeter` (5) |
| 2 | 15 | `cyclic-quadrilateral` (9), `arc-midpoint-on-bisector` (3), `angle-in-semicircle` (3), `two-intersecting-circles` (3), `perpendicular-from-center-to-chord` (3) |

**For task 21's boss ladder:**
- Up to about 5 kyu, the object is a triangle with parallels, an isosceles axis or a right angle. Similarity does the work.
- At 4 kyu, circles start to matter: chords, tangents and the first cyclic quadrilaterals.
- At 3 and 2 kyu, the cyclic quadrilateral dominates, along with pairs of intersecting circles and arc midpoints. It appears in 9 of the 15 problems at 2 kyu.

**The named olympiad configurations barely occur.** `incenter-excenter-lemma` appears 3 times, `symmedian` twice, `mixtilinear-incircle`, `simson-line`, `orthic-triangle` and `orthocenter-reflection` once each. `miquel-point`, `nine-point-circle`, `euler-line` and `complete-quadrilateral` don't appear. The ladder's top rungs must come from the olympiad wave, not from AIME.

The techniques on geometry problems are mostly computational: `pythagorean-theorem` (99), `coordinate-bash` (94), `similar-triangles` (94), `law-of-cosines` (63), `area-by-decomposition` (46), `right-triangle-trigonometry` (40), `law-of-sines` (35), `area-ratios` (34), `vector-method` (33), `angle-chasing` (33). `coordinate-bash` appears on nearly a third, often as a derived route, which is one reason a less computational route is a good target for the "change the route" recipe.

## Pilot and re-run

Before the full run, 31 problems went through both passes twice, once with the original prompt and once after tightening the definition of the primary technique.

| Measure | First run | Re-run |
|---|---|---|
| Topic differs | 3% | 0% |
| Techniques differ (Jaccard below 0.5) | 13% | 16% |
| Primary technique differs | 23% | 29% |
| The stricter rule | 35% | 42% |
| Kyu differs | 19% | 10% |

The tighter prompt didn't help, and the stricter rule missed its 25% target both times, which is why Kevin moved the measure to set overlap. That rule was therefore set after seeing the data. Classic problems also moved easier nearly every time, which led to their one-kyu-easier start.

## Known defects in the data

- `AIME-2000-II-05` has a copy of `AIME-2000-II-04`'s statement, so the real problem is missing from the corpus. Its record is flagged, has no family, and shouldn't be used.
- The 15 problems of the 2000 II paper have no collected solutions or answers. Their answers are derived and unverified against a source, though both passes agreed wherever both ran.
- Analysts flagged 60 problems with slips in the collected solutions or statements, 8 of them in the statement. None changes an answer apart from the one above. The private list is `reports/aime-source-defects.md`, for task 02.
