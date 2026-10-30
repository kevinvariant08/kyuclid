# 09. Build the proof-problem pipeline (3–1 kyu)

## Goal
Build a bank of olympiad proof problems for 3, 2 and 1 kyu. Each comes with a model solution and a seven-mark rubric. Target: **30 at 3 kyu, 20 at 2 kyu and 10 at 1 kyu** to start with. Quality matters far more than quantity here: one wrong 1 kyu problem damages trust more than a hundred good 5 kyu ones.

## Depends on
04 (the standard, including the proof section) and 07 (review queue).

## Read first
- `docs/problem-standard.md` §8, `tasks/README.md` and the open decision in it about famous problems.
- Kevinvariant's Proof marker (`kevinvariant08.github.io/marker.html` and its repo) for how it prompts a model to mark written solutions. Reuse what works.

## Spec
1. **Corpus (private).** Add BMO1 (questions 4–6), BMO2, and the IMO and EGMO shortlists for the last 15 years to `mathwars-corpus`, with official or AoPS solutions. Run the task 03 analysis, adding a `proof_skeleton` field: the key lemma or construction, in abstract form.
2. **Two sources of problems:**
   - **Original.** Generate with `claude-opus-5-5` from a `proof_skeleton` and a variation recipe (task 06). The output is the statement, the model solution and the rubric.
   - **Classical, if Kevin allows it.** Famous problems, restated in MathWars' own words with attribution in `provenance`, such as IMO 1988 P6 or Erdős–Ginzburg–Ziv. Each needs Kevin's explicit OK.
3. **Verification.** Answers can't be checked, so the gate is different:
   - **Truth.** Three independent attempts to *disprove* the statement: a search for counterexamples with a computer where that is possible (for example, checking number-theory claims up to 10⁶), plus a model looking for a counterexample.
   - **Solvability.** Three independent blind proof attempts. At least one must be judged complete by a separate marker using the rubric. If none succeeds, either the problem is too hard or the statement is wrong, so flag it.
   - **Solution audit.** A critic checks the model solution line by line.
   - **Rubric check.** The rubric totals 7 and awards partial credit for real milestones. Test it by marking two deliberately flawed proofs: they should score in the expected range.
   - **Originality.** As in task 05, against the proof corpus.
4. **Review.** Every proof problem needs Kevin's sign-off in the task 07 queue. Show the counterexample search, the blind attempts and their marks.

## Acceptance criteria
- 60 approved proof problems, or fewer if quality demands it, with the shortfall explained.
- For each one there are counterexample-search logs, at least one blind proof marked complete, and a rubric that has been tested.
- Kevin has signed off every problem individually.

## Out of scope
Submitting and peer-reviewing users' proofs on the site (task 16).
