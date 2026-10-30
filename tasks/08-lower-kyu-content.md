# 08. Extend the pipeline to 8–6 kyu

## Goal
Fill the beginner and intermediate belts (8, 7 and 6 kyu) with original problems of the right difficulty, using the same corpus → analyse → generate → verify → review pipeline. Target: **at least 60 problems per kyu** across all four topics.

## Depends on
06 (generator) and 07 (review queue). It reuses 02–05.

## Read first
- Tasks 02, 03, 05 and 06, and `docs/problem-standard.md`.

## Spec
1. **Corpus.** Add these to the private `mathwars-corpus` with the task 02 record format and checks:
   - **AMC 8**, 2012–2026 (25 problems a year).
   - **AMC 10A/10B**, 2012–2026 (25 problems a paper). Record the answer letter and the value.
   - **UKMT JMC, IMC and SMC**, the last 10 years, if a lawful source is available. Ask Kevin, who may have the papers. Skip any exam you can't source cleanly.
2. **Analysis.** Run task 03 on the new exams. Initial kyu from position:
   - AMC 8 problems 1–10 are 8 kyu, 11–20 are 7 kyu and 21–25 are 6 kyu.
   - AMC 10 problems 1–10 are 7 kyu, 11–20 are 6 kyu and 21–25 are 5 kyu.
   - UKMT positions get mapped similarly. Write the mapping down and justify it.
3. **Answer format.** Lower-kyu MathWars problems are **free response**, not multiple choice. When the inspiration was multiple choice, the generated problem must still have a single, checkable answer and must not depend on the options for elimination.
4. **Difficulty calibration.** Refit the task 05 difficulty mapping with 8–6 kyu corpus examples. Weaker models solve these easily, so use a smaller model, `claude-haiku-5-5`, plus solve time as the signal. Document the method.
5. Then run generation, verification and review as in tasks 06 and 07: pilot 30, wait for Kevin's go-ahead, then the full run.

## Acceptance criteria
- At least 60 approved problems at each of 8, 7 and 6 kyu, with every topic at least 10 per kyu.
- The calibration report shows estimated versus target kyu on held-out corpus problems, with at least 80% within one kyu.
- No corpus text appears in the public repo.

## Out of scope
Proof problems. 5 kyu and harder, which task 06 covers.
