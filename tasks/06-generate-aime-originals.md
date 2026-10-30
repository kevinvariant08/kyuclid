# 06. Generate original AIME-level problems (5–3 kyu)

## Goal
Use the analysed AIME corpus to produce a large set of **original** problems at matched difficulty. Each one should teach the same idea as an AIME problem without being a copy of it. Target: **at least 300 problems that pass verification**, spread across 5, 4 and 3 kyu and all four topics.

## Depends on
03 (analysis), 04 (standard) and 05 (verification gate). It feeds 07 (review queue).

## Read first
- `docs/problem-standard.md`, `docs/aime-analysis.md` and `data/taxonomy.json`.
- `pipeline/verify/` and its README.
- `tasks/README.md`, rules 1, 2 and 5.

## Deliverables
`pipeline/generate/`, which runs as:

```
python -m pipeline.generate --from AIME-2019-I-07 [--n 2]
python -m pipeline.generate --plan plan.json        # batch
```

### How one problem is made
1. **Input.** Take one corpus analysis record: `core_idea`, `key_steps`, `traps` and `kyu`. Give the generator the original statement too, labelled "for calibration only, do not reuse its setting, objects, numbers or phrasing".
2. **Pick a variation recipe**, chosen at random from those that suit the idea, and record which one in the draft:
   - **Transplant.** Use the same technique on a different object. For example, Vieta on a cubic becomes Vieta on a trigonometric identity.
   - **Invert.** Ask for what the original problem gave.
   - **Combine.** Merge the core idea with a second technique from the same kyu band.
   - **Generalise then specialise.** Take the family the idea belongs to and pick a fresh member of it.
   - **New context.** Use the same structure on a combinatorial or geometric model that the original didn't use.
   - A pure number swap, or the same story with renamed objects, is **never** acceptable.
3. **Generate** with `claude-opus-5-5`, with structured output that matches the draft format from task 05: statement, answer, solution, 2–3 hints, `check_program`, `subtopics`, target `kyu`, recipe and `inspired_by`. Ask for three candidates and keep the one the model rates the most interesting.
4. **Verify.** Run it through `pipeline.verify`. On a fail, feed the failure reason back for up to two repair attempts. After that, discard it and log why.
5. **Save** passing drafts to `review/pending/<id>.json` together with their verification report. The `inspired_by` field and the original text never go in the public repo: keep the mapping in `mathwars-corpus/generated_map.jsonl`.

### The batch plan
- Cover every corpus problem once. Then add extra runs for under-represented techniques (from the task 03 gaps list) until each kyu × topic cell has at least 20 passing problems.
- Write a geometry problem with a figure only after task 10 lands. Until then, pick recipes that need no diagram, or describe the figure fully in words.

### Pilot first
Run 30 inputs, 10 per kyu. Report:
- The pass rate at each verification step.
- The cost per passing problem.
- Five problems you think are excellent and five that passed but are weak, with reasons.

**Stop and wait for Kevin's go-ahead** before the full run. Adjust the prompts based on the review rejections from task 07.

## Acceptance criteria
- 300 or more drafts pass verification and sit in `review/pending/`, covering every kyu × topic cell.
- A run log records the inputs, recipes, pass and fail reasons, models and cost.
- Kevin's review of a random 20 accepts at least 15.
- No published file contains corpus text. Check with a `git grep` for 10 distinctive corpus phrases.

## Out of scope
Building the review UI (07), lower kyu (08), proofs (09).
