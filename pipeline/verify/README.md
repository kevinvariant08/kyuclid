# The verification gate

Every new problem must pass this before a human sees it. It catches wrong answers, ambiguous statements, mis-rated difficulty and disguised copies of contest problems.

```
python -m pipeline.verify draft.json [--report out/report.json]
python -m pipeline.verify --batch dir/ [--report out/batch] [--concurrency 4]
```

It prints one line: `PASS`, `FAIL <check>: <reason>` or `INVESTIGATE <check>: <reason>`. If a model call fails it prints `ERROR <check>: <reason>`, which is not a judgement on the draft. The exit code is 0 for all PASS, 1 for any FAIL or INVESTIGATE, and 3 for any ERROR.

## Setup

- Python 3.12+ with `pip install -r pipeline/verify/requirements.txt`.
- Node 20+ with `npm ci`. That installs `mathjax-full`, the same version the site loads, for the LaTeX dry run. Without it the gate falls back to a balance check, and the report says so.
- The Claude Code CLI, signed in.
- `KYUCLID_CORPUS` set to the private corpus. `MATHWARS_CORPUS` also works; if both are set, `KYUCLID_CORPUS` wins. Without either, originality compares with the bank only, and the report says so.

## A draft

A problem JSON in the `schema/problem.schema.json` format, plus fields for the gate that are removed before validation:

| Field | Meaning |
|---|---|
| `answer` | The plain answer. Answer problems only. |
| `check_program` | Python that prints the answer on its last line. Answer problems only. |
| `inspired_by` | Private corpus ID. The inspiration is always shown to the originality judge. |
| `core_idea` | Optional abstract idea. If missing, and the corpus has core ideas, Haiku writes one. |
| `variation_recipe` | Task 06's record of its recipe. The gate ignores it. |

## The checks

They run in this order, and the first failure stops the run. `--keep-going` runs everything except after a schema failure.

| # | Check | How | Cost |
|---|---|---|---|
| 1 | `schema` | The site's schema, `answer_hash` against `answer` through `js/lib/answers.js`, and a MathJax dry run | free |
| 8 | `standard` | The automatable rules: answer range, hint count, a hint giving away the answer, UK spelling, contest names, the private ID leaking | free |
| 7a | `originality_lexical` | Automatic fail above the fitted similarity threshold | free |
| 2a | `computational` | The program runs in the sandbox and must print the key. A static check rejects programs that compute nothing | free |
| 2b | `program_judge` | Sonnet: does the program really compute this quantity, or restate the solution? | 1 call |
| 3 | `blind_solves` | Five Sonnet, one Haiku, one Opus, from the statement alone | 7 calls |
| 4 | `well_posedness` | Opus critic | 1 call |
| 5 | `solution_audit` | Opus critic | 1 call |
| 6 | `difficulty` | Solve rate and tokens mapped to a kyu | free |
| 7b | `originality` | Opus judge on the five nearest problems and the inspiration, plus "is this a known problem?" | 1 call |

The brief's order puts `standard` and originality last. The free parts run early here so a draft they would fail costs nothing. If several checks fail under `--keep-going`, the verdict names the first in the brief's order.

Blind solves: at least 4 of 7 on the key passes. If 4 or more agree on something else the result is INVESTIGATE (wrong key or ambiguous). With no majority it's also INVESTIGATE (too hard or ambiguous; the brief doesn't define this case). All 7 right at very few tokens fails as too easy, at 5 kyu or harder. INVESTIGATE doesn't stop the run, so a reviewer sees what the critics say too.

Proof problems skip checks 2, 3 and 6. Task 09 adds its own.

Classical problems skip the originality checks. One from the book passes. One quoting a contest (its `source` names one) fails under rule 1. Any other, such as a named theorem, gets INVESTIGATE, because whether it can appear with attribution is Kevin's open decision.

## Models and independence

The brief asks for a second opinion from a different model family. Only Claude is available here, so independence comes from different Claude models: Haiku 5.5 and Opus 5.5 alongside Sonnet 5.5. These errors are less independent than another family's would be: models that share training can share a misreading. To change the mix, edit `SOLVERS` and `ROLES` in `config.py`.

## Backends

- **`cli` (default).** `claude -p` on Kevin's plan, at no API cost. Each call runs from an empty temp folder with no tools, no settings and no session, so solvers can't see this repo or a solution. A probe confirmed what a call does receive: the account email and basic environment details. `ANTHROPIC_API_KEY` is removed from the child's environment, so a stray key can't bill.
- **`api`.** `--backend api`, which costs money. It's never chosen automatically, even if a key is set, and refuses to start without `ANTHROPIC_API_KEY`. It needs `pip install anthropic`. **It hasn't been run**: there's no key here, so only its refusal path is tested.

Replies are cached in `out/cache/` by model and prompt, so a re-run costs nothing and resumes after a plan limit. Prompts holding corpus text are never cached. If the plan limit is hit, a batch stops starting drafts and reports it. `--no-cache` repeats the calls.

## Reports

`out/report.json`, or one file per draft plus `_summary.json` with `--batch`. Each holds every check's result and evidence, model IDs, token counts and usage. `out/` is gitignored.

**Usage.** `api_equivalent_usd` is what the calls would cost at API list prices. On the plan it's an estimate of usage, not money spent. `_this_run` leaves out cached calls.

## Private corpus

Corpus text may reach a judge's prompt, but it must never reach a report, the cache or this repo:

- Reports hold corpus IDs and similarity scores only.
- A judge's reason is removed if it shares 8 consecutive words with a neighbour.
- An unreadable judge reply isn't quoted.
- `fit_difficulty.py` stores numbers and IDs only.
- A test scans everything in `pipeline/` for 10-word runs from the corpus. It runs when a corpus is configured, and it has already caught one stock phrase in a fixture of mine.

## The sandbox

No network, a 60-second limit (plus up to 30 seconds for importing sympy and numpy), 2 GB of memory, one process, and only `sympy`, `numpy` and allow-listed standard modules. `random` isn't allowed, because a sampled answer isn't exact.

**It is best effort, not a security boundary.** Windows without admin rights has no network namespace, so these limits are enforced from inside the Python process by an audit hook, plus a static check and a Windows job object. That stops a generated program from wandering off by accident. It won't stop one written to escape. Only run drafts from this pipeline. Task 17 (community authoring) must not run untrusted programs through this; it needs a real container.

## Originality, and what it can't do

There's no embeddings endpoint on the plan, so "embedding" means local TF-IDF over words and character n-grams, with numbers and single-letter variables masked. `core_idea` is compared the same way once task 03 writes `<exam>_analysis.jsonl`; no code change is needed.

The automatic-fail threshold comes from `fit_similarity.py` and sits above both the most similar same-technique pair and the 97th percentile of what real corpus problems reach against each other. See `similarity.json`.

**TF-IDF catches copies, not reskins.** A reskin in a new setting shares few words with its source, so retrieval can miss it, and then the judge never sees the source. The judge's "known problem" question works from memory and partly covers this. `core_idea` matching should help once it exists. Until then, a reskin of an obscure corpus problem in a new setting can get through unless `inspired_by` names it. Task 06 always sets that, so the generator's own inspiration is always examined.

**A routine exercise in a story isn't flagged.** `reskin-gauss`, the sum 1 to 40 told as a runner's laps, passes. The judge calls it routine with no specific source. That fits rule 2's purpose, but it means low-kyu problems need the reviewer's eye for staleness.

**At low kyu, the judge can be strict.** Simple problems have few possible structures, and it matched one of my two-equation warm-ups to a real AMC 10 problem with the same structure. Task 08 should watch how often this rejects honest 8 to 6 kyu drafts.

## Difficulty, and how far to trust it

`thresholds.json` is **provisional**: 30 corpus problems, with kyu taken from the contest position table in task 03. While it's provisional, a mismatch of more than one kyu gives INVESTIGATE rather than FAIL.

The ruler is weak. The models solve nearly every AIME problem 7/7, so only token use separates kyus, and kyus 6 to 3 overlap heavily. They've probably seen these contests, which makes them look easier than they'd find a fresh problem. Treat the estimate as "warm-up or not" until the full fit:

```
python -m pipeline.verify.fit_difficulty --per-kyu 10 --final
```

That's about 420 model calls, the 60 problems the brief asks for. Task 03's real kyus should replace the position table first. Solve data from task 18 is the better long-term source. `--refit` recomputes from the saved results with no model calls.

## Standard rules

`docs/problem-standard.md` doesn't exist yet, so `standard.py` follows the rules in `tasks/04-problem-standard.md`. When task 04 lands, compare it with that document's appendix of automatable rules.

## Tests

```
python -m pipeline.verify.tests.suite                 # regenerate tests/drafts and expected.json
python -m unittest discover -s pipeline/verify/tests -t .
python -m pipeline.verify --batch pipeline/verify/tests/drafts --report out/suite
python -m pipeline.verify.tests.score_live out/suite
```

The unit tests use a scripted backend: no models, no money, about five minutes because of the sandbox runs. The last two commands are the live run. All drafts are invented or reskin famous public puzzles; none comes from the corpus.

The seeds:

```
python -m pipeline.verify.run_seeds --check-only      # free: keys against hashes, programs in the sandbox
python -m pipeline.verify.run_seeds                   # writes SEED_VERDICTS.md
```

## Measured usage

From the live runs on 30 October 2026. Figures are API-equivalent dollars, so on the plan they measure usage and no money is spent. The CLI doesn't report a share of the plan's allowance, so these can't be turned into a percentage of it.

| What | Calls | Output tokens | API-equivalent |
|---|---|---|---|
| A draft that fails a free check (25 of the 55 in the suite) | 0 | 0 | $0 |
| A draft that goes through every check (median of 15) | 11 | 2,600 | $0.10 |
| The same, on a hard problem (`mis-rated-hard`) | 11 | 126,000 | $0.91 |
| Seed problems, every check run (mean of 21) | 9 | 2,700 | $0.09 |
| Blind solves alone on an AIME or AMC problem (mean of 30) | 7 | 5,200 | $0.07 |
| The judge on one reskin pair (mean of 40) | 1 | 180 | $0.013 |

Expect generated 5 to 3 kyu problems to sit between the second and third rows, because harder problems take far more reasoning.

The output cap is 16,000 tokens per solve, but the CLI retries a capped reply up to four times, so one call can use up to 64,000. There's no flag to stop that. Haiku hit it on the hard problem, which cost $0.03. A Sonnet call hitting it would cost about $0.64, though the hardest Sonnet solve so far used 10,400 tokens.

Live results: 55 of 55 suite drafts got their expected verdict. Given only the pair, the judge caught 20 of 20 reskins and raised no false alarm on 20 same-technique pairs. Those pairs are ones I wrote, so treat that as a check that the prompt works, not as its real accuracy. Model verdicts vary between runs: the suite's expected verdicts allow more than one check where several would rightly reject a draft.
