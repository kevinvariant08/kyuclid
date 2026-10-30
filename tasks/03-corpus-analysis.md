# 03. Analyse and tag the AIME corpus

## Goal
For every corpus problem, record the mathematics underneath it: topic, techniques, the core idea in abstract form, the traps, and how hard it is. Then summarise what an AIME looks like at each problem position. This is what generation (task 06) imitates and what the problem standard (task 04) calibrates against.

## Depends on
02, the corpus.

## Read first
- `tasks/README.md` (the rules), `tasks/02-aime-corpus.md` (the record format).
- `mathwars-corpus/corpus/aime.jsonl`.

## Deliverables
1. **A controlled vocabulary** at `mathwars/data/taxonomy.json`. This file is public, since it holds no problem text.
   - Topics: `A`, `C`, `G`, `N`.
   - About 60–100 subtopics and techniques, for example `vieta`, `telescoping`, `complex-roots-of-unity`, `inclusion-exclusion`, `bijection`, `recursion-linear`, `expected-value-linearity`, `power-of-a-point`, `similar-triangles`, `coordinate-bash`, `trig-ceva`, `lte`, `crt`, `orders-mod-n`, `legendre`, `floor-sums`.
   - Each entry gets a one-line definition. Build the list bottom-up from the corpus, then merge near-duplicates.
2. **A per-problem analysis** at `mathwars-corpus/corpus/aime_analysis.jsonl`, which stays private:
   ```json
   {"id":"AIME-2019-I-07","topic":"N","subtopics":["logarithms","prime-factorisation"],
    "core_idea":"Two coupled log equations reduce to exponent equations on primes; count divisors.",
    "key_steps":["...", "..."], "traps":["forgetting ..."],
    "solution_length":"short|medium|long", "computation_load":"low|medium|high",
    "kyu":4, "kyu_reason":"AIME position 7, one non-obvious step", "has_figure":true}
   ```
   - `core_idea` must be abstract: no numbers and no story from the problem. It should describe a family of problems, not this one.
   - Starting `kyu` from the paper position: problems 1–5 are 5 kyu, 6–10 are 4 kyu and 11–15 are 3 kyu. Adjust by at most one kyu, with a reason. (13–15 on hard papers may be 3 kyu at the top of the range, but AIME is never 2 kyu.)
3. **The method.** Analyse each problem with `claude-opus-5-5` using structured output against the taxonomy. Give it the problem and the AoPS solutions (fetched politely into the corpus repo if they aren't already there). Then have a second pass with a different model check 10% of the records. Record where the two disagree.
4. **A public report** at `mathwars/docs/aime-analysis.md`, with no problem text:
   - The topic mix by position (1–5, 6–10, 11–15) and by year.
   - The 30 most frequent techniques, and which positions they appear at.
   - What separates a 4 kyu problem from a 3 kyu one, in concrete terms: the number of non-routine steps, the computation load, the use of a figure.
   - Any gaps: techniques that appear at most twice, where generation will need care.

## Acceptance criteria
- Every corpus problem has an analysis record that validates against the taxonomy.
- Kevin spot-checks 15 records (put a checklist in the PR) and agrees with at least 13 of them.
- The second-model disagreement rate on topic is under 10%, and the disagreements are resolved.
- The report exists and contains no problem text.

## Out of scope
Generating problems. Other exams.
