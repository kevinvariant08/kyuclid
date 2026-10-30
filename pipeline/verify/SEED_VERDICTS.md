# Seed problem verdicts

From `python -m pipeline.verify.run_seeds`, which runs every check even after a failure. The verdict names the first failure in the brief's order; the last column lists any others. Judges' full reasons are in the private reports under `out/seeds/`.

| Problem | Verdict | Blind solves | Estimated kyu | Other failures |
|---|---|---|---|---|
| circle-in-the-square | FAIL originality: known problem: Classic puzzle | 7/7 | 7 | standard: hint count: 1, the standard asks for two or three (and 1 more); difficulty: estimated 7 kyu, target 5 kyu (thresholds are provisional) |
| closest-approach | FAIL standard: hint count: 1, the standard asks for two or three | 7/7 | 7 | difficulty: estimated 7 kyu, target 5 kyu (thresholds are provisional) |
| cube-the-reciprocal | FAIL standard: hint count: 1, the standard asks for two or three | 7/7 | 8 |  |
| divisor-census | FAIL originality: reskin of AMC8-2018-18 | 7/7 | 8 |  |
| domino-corridor | FAIL originality: known problem: Classic domino tiling of a 2-by-n board (Fibonacci numbers) | 7/7 | 7 | standard: hint count: 1, the standard asks for two or three |
| egyptian-pairs | FAIL originality: known problem: Diophantine reciprocals, 1/x + 1/y = 1/n (classic; cf. Project Euler 108) | 7/7 | 7 | standard: hint count: 1, the standard asks for two or three; blind_solves: too easy for 5 kyu: 7/7 solved it at about 115 tokens; difficulty: estimated 7 kyu, target 5 kyu (thresholds are provisional) |
| egz | INVESTIGATE originality: classical (Erdős, Ginzburg and Ziv, 1961), not original: whether it can appear with attribution is Kevin's decision | n/a | n/a |  |
| factorial-sandwich | FAIL originality: quotes a contest problem (AIME 1990, Problem 11) and isn't from the book, which rule 1 forbids | 7/7 | 6 | difficulty: estimated 6 kyu, target 3 kyu (thresholds are provisional) |
| floor-staircase | FAIL originality: quotes a contest problem (AIME 1985, Problem 10) and isn't from the book, which rule 1 forbids | 7/7 | 5 |  |
| last-two-digits | FAIL standard: hint count: 1, the standard asks for two or three | 7/7 | 7 | difficulty: estimated 7 kyu, target 5 kyu (thresholds are provisional) |
| neither-fizz-nor-buzz | FAIL originality: reskin of AMC8-1991-09 | 7/7 | 7 | standard: hint count: 1, the standard asks for two or three |
| nesbitts-guard | INVESTIGATE originality: classical (Nesbitt, 1903), not original: whether it can appear with attribution is Kevin's decision | n/a | n/a |  |
| polygon-from-one-angle | FAIL standard: hint count: 1, the standard asks for two or three | 7/7 | 8 |  |
| prime-power-desert | FAIL originality: quotes a contest problem (IMO 1989, Problem 5) and isn't from the book, which rule 1 forbids | n/a | n/a |  |
| round-table-no-neighbours | FAIL originality: known problem: Independent sets in a cycle graph (Lucas numbers; Kaplansky's lemma) | 7/7 | 7 | difficulty: estimated 7 kyu, target 4 kyu (thresholds are provisional) |
| square-hunting | FAIL originality: near-duplicate of AIME-1999-03: similarity 1.00 is over the 0.87 limit | 7/7 | 6 | standard: answer range: 4 kyu answers are integers from 0 to 999, got 1196; difficulty: estimated 6 kyu, target 4 kyu (thresholds are provisional) |
| the-13-14-15-triangle | FAIL originality: known problem: 13-14-15 Heronian triangle inradius (classic) | 7/7 | 7 |  |
| there-and-back | FAIL standard: hint count: 1, the standard asks for two or three | 7/7 | 8 |  |
| twenty-to-four | FAIL originality: reskin of AMC8-2003-20 | 7/7 | 7 |  |
| vieta-leap | FAIL originality: quotes a contest problem (IMO 1988, Problem 6) and isn't from the book, which rule 1 forbids | n/a | n/a |  |
| zeros-of-2026 | FAIL originality: known problem: Classic trailing zeros of a factorial (Legendre's formula) | 7/7 | 7 |  |

## Usage

193 model calls across 21 problems, 2667 output tokens a problem, about $0.0839 a problem at API list prices. On the plan this is usage, not money.
