# Corpus analysis

**Status: pilot only.** This covers the AIME pilot. The full synthesis the task 03 brief asks for (frequency by kyu band, idea families, gaps, the geometry deep-dive) comes after the full run. No problem text appears here: contest problems stay in the private corpus.

## Taxonomy draft

`data/taxonomy.json` is version 0.2.0-draft, with 207 techniques and 51 geometry configurations. Seven of the techniques are marked `legacy` because only the seed problems need them, which leaves 200 for tagging.

It was built in three steps:
1. An Opus agent tagged 150 AIME problems, stratified by position and era, and named what it saw.
2. Near-duplicates were merged. Where the mined name differed from the brief or the seed problems, the existing spelling won (`crt`, `sfft`, `coordinate-bash`).
3. Tools the sample missed but later waves need were added as `seeded`, such as `zsigmondy` and `spiral-similarity`. Tags the pilot asked for are `pilot-proposed`.

`sample_count` counts problems in the 150-problem sample, so a seeded or pilot-proposed tag shows 0.

## Pilot method

- 30 problems, 10 from each of positions 1–5, 6–10 and 11–15, 9 classic and 21 modern, with geometry oversampled by keyword. One problem from the paper with no collected solutions was added as a test case, making 31. The ids and seed are in the private repo.
- First pass: `claude-opus-5-5`. Second pass: `claude-sonnet-5-5`, blind to the first pass.
- The disagreement rule was fixed in code before any results were read. Topic disagrees if the topics differ. Techniques disagree if the primary technique differs or the Jaccard index of the two sets is below 0.5.

## Pilot results

| Measure | Result | Target |
|---|---|---|
| Topic disagreement | 3% (1 of 31) | under 10% |
| Technique disagreement | 35% (11 of 31) | under 25%: **missed** |
| Primary technique differs | 23% (7 of 31) | |
| Jaccard below 0.5 | 13% (4 of 31) | |
| Mean Jaccard | 0.65 | |
| Configuration sets differ | 3 of 6 records where either pass tagged one | |
| Kyu differs | 19% (6 of 31), never by more than one | |

Every disagreement was resolved by reading both records against the problem. Merging one near-duplicate pair afterwards only moves technique disagreement to 32%, so the miss comes mainly from which tag is listed first: in 7 of the 11 cases the passes broadly agreed on the set but not on the primary.

Kyu after resolution, measured against the starting value from position:

| Era | Moved easier by one | Unchanged | Moved harder |
|---|---|---|---|
| Classic (9) | 8 | 1 | 0 |
| Modern (22) | 5 | 17 | 0 |

Position overrates classic problems by about one kyu, and the one-kyu cap may be binding there. Nothing moved harder.

## Cost

| Stage | Model | Problems | Tokens | Time | Per problem |
|---|---|---|---|---|---|
| Taxonomy mining | Opus 5.5 | 150 | 246,821 | 9.7 min | 1.6k tokens |
| First pass | Opus 5.5 | 31 | 209,850 | 18.6 min | 6.8k tokens, 36 s |
| Second pass | Sonnet 5.5 | 31 | 193,857 | 9.3 min | 6.3k tokens, 18 s |

No API money was spent.

## Geometry configurations for review

Named olympiad configurations barely appeared in the sample: the nearest are `arc-midpoint-on-bisector` and `circumcircle-tangent-intersection`, once each. AIME geometry leans on elementary configurations, so the olympiad list stays seeded until the olympiad wave.

### Observed in the sample

| Slug | Definition | Sample count |
|---|---|---|
| `perpendicular-from-center-to-chord` | The perpendicular from a circle's centre bisects a chord and forms a right triangle with the radius. | 5 |
| `special-right-triangles` | Right triangles with standard acute angles and known side ratios. | 5 |
| `two-tangents-from-a-point` | Two tangents to a circle from an external point, equal in length with the centre on the bisector. | 5 |
| `isosceles-triangle-axis` | An isosceles triangle whose apex altitude is also a median and an angle bisector. | 4 |
| `plane-section-of-solid` | The polygon or curve in which a plane cuts a polyhedron or cylinder. | 4 |
| `angle-in-semicircle` | An angle subtended by a diameter is a right angle. | 3 |
| `cyclic-quadrilateral` | Four concyclic points, giving supplementary opposite angles and equal subtended angles. | 3 |
| `incircle-and-semiperimeter` | A triangle or tangential polygon with its incircle, whose tangency points split sides into tangent lengths. | 3 |
| `incircles-of-cevian-subtriangles` | The incircles or incenters of the two subtriangles created by a segment from a vertex to the opposite side. | 3 |
| `isosceles-trapezoid` | An isosceles trapezoid, decomposed by altitudes from the shorter base. | 3 |
| `nested-squares` | A square inside another square, with congruent or similar right triangles in the corners. | 3 |
| `parallel-segments-in-triangle` | Segments parallel to a triangle's side, including midlines, cutting similar triangles. | 3 |
| `regular-polygon-central-triangles` | A regular polygon divided into isosceles triangles from its centre, with vertices on a circumcircle. | 3 |
| `tangent-spheres-on-plane` | Spheres resting on or against a plane and tangent to each other or to a second plane, with centres at known heights. | 3 |
| `circular-segment` | The region between a chord and its arc, equal to a sector minus a triangle. | 2 |
| `incenter-angle-formula` | The angle at an incenter subtending a side, a right angle plus half the opposite angle. | 2 |
| `mutually-tangent-circles` | Circles tangent internally or externally, whose centres and tangency point are collinear. | 2 |
| `right-triangle-altitude` | The altitude to the hypotenuse creates similar triangles and geometric-mean relations. | 2 |
| `trirectangular-corner` | A corner of a box where three mutually perpendicular edges meet, giving a pyramid cut from a cube. | 2 |
| `two-intersecting-circles` | Two circles meeting at two points, with a common chord or a line through an intersection point. | 2 |
| `arc-midpoint-on-bisector` | An internal angle bisector meets the circumcircle at the midpoint of the opposite arc, on the side's perpendicular bisector. | 1 |
| `circumcircle-tangent-intersection` | The meeting point of the tangents to a triangle's circumcircle at two vertices. | 1 |
| `circumsphere-of-pyramid` | The sphere through all vertices of a pyramid, with its centre on the axis. | 1 |
| `common-external-tangent` | A line tangent to two circles, with radii to the tangency points parallel. | 1 |
| `concentric-annuli` | Concentric circles bounding annular regions, whose areas are differences of squares of radii. | 1 |
| `fixed-angle-arc-locus` | Points seeing a fixed segment under a constant angle lie on a circular arc. | 1 |
| `isosceles-tetrahedron` | A tetrahedron with congruent faces, inscribable in a rectangular box with edges as face diagonals. | 1 |
| `median-to-hypotenuse` | The median to the hypotenuse equals half the hypotenuse, making the midpoint the circumcentre. | 1 |
| `regular-tetrahedron` | A regular tetrahedron, with a known volume and a square midsection between opposite edges. | 1 |
| `trapezoid-extended-legs` | A trapezoid whose legs are extended to meet, forming similar triangles. | 1 |
| `triangle-from-altitudes` | A triangle specified by its altitudes, with sides inversely proportional to them. | 1 |

### Proposed by the pilot

| Slug | Definition | Sample count |
|---|---|---|
| `equiangular-polygon` | A polygon with all angles equal, so that its sides are vectors with fixed turning angles. | 0 |
| `rhombus-tiling` | Congruent rhombi around a central rhombus, sharing its sides. | 0 |
| `square-in-right-triangle` | A square inscribed in a right triangle, either at the right angle or on the hypotenuse. | 0 |
| `squared-rectangle` | A rectangle dissected into squares, whose sizes add along shared edges. | 0 |

### Seeded, not yet seen

| Slug | Definition | Sample count |
|---|---|---|
| `apollonius-circle` | The locus of points with a fixed ratio of distances to two points. | 0 |
| `centroid-medians` | Medians meeting at the centroid, which splits them in a fixed ratio and the area equally. | 0 |
| `complete-quadrilateral` | Four lines and their six intersection points, with their diagonals. | 0 |
| `euler-line` | The line through the circumcenter, centroid and orthocenter, with its fixed ratio. | 0 |
| `excircle` | A circle tangent to one side and the extensions of the other two, with its tangent lengths. | 0 |
| `harmonic-quadrilateral` | A cyclic quadrilateral with equal products of opposite sides. | 0 |
| `incenter-excenter-lemma` | The midpoint of an arc is equidistant from two vertices, the incenter and the excenter. | 0 |
| `medial-triangle` | The triangle of side midpoints, homothetic to the original. | 0 |
| `miquel-point` | The common point of the four circumcircles of a complete quadrilateral. | 0 |
| `mixtilinear-incircle` | A circle tangent to two sides of a triangle and internally to its circumcircle. | 0 |
| `nine-point-circle` | The circle through the side midpoints, altitude feet and orthocenter-vertex midpoints. | 0 |
| `orthic-triangle` | The triangle of altitude feet, whose incenter is the orthocenter. | 0 |
| `orthocenter-reflection` | Reflections of the orthocenter in the sides and midpoints lie on the circumcircle. | 0 |
| `pitot-tangential-quadrilateral` | A quadrilateral with an incircle, whose opposite sides have equal sums. | 0 |
| `simson-line` | The feet of perpendiculars from a point on the circumcircle are collinear. | 0 |
| `symmedian` | The reflection of a median in the angle bisector, and the tangent-intersection construction. | 0 |
