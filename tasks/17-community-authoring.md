# 17. Community problem authoring and beta

## Goal
Let strong players propose problems, as Codewars lets users write kata, so that the bank keeps growing without Kevin writing everything. Quality is protected by the verification gate, beta voting and Kevin's approval.

## Depends on
05 (verification gate) and 13 (accounts).

## Spec
1. **Who can author:** players at 4 kyu or above. New authors are limited to two problems in beta at a time.
2. **The authoring form** (`#create`) has:
   - Fields for the statement, answer, solution, 1–3 hints, topic, subtopics and suggested kyu, with a live preview.
   - A "Source" field: original or adapted. Adapted problems must name the source and are reviewed for permission.
   - A checkbox confirming that the author wrote the problem and has the right to publish it.
3. **Automatic checks on submit.** Run the verification gate (05) on the server, through a queue, because it calls models and costs money: originality, blind solves, well-posedness and difficulty estimate. Since a community answer can't come with a check program, require at least 5 of 7 blind solves to agree instead. Show the author the results and let them fix things.
4. **Beta.** Problems that pass enter `status: "beta"` and are shown to players who opt into beta problems. Players who solve one vote on its kyu ("easier / about right / harder") and its quality ("good problem / not for me"). Beta solves earn half points.
5. **Promotion.** Once a problem has 30 solves, 70% approval or more, and a kyu vote that has settled, Kevin gets it in a queue to promote to `ranked` with its final kyu. Its rank points then count fully, retroactively.
6. **Authors earn honour points** for each solve of their ranked problems.
7. **Reports and removal.** Players can report a problem (wrong answer, ambiguity, copied from a contest), and three reports pull it back to review.

## Acceptance criteria
- A test author can submit, get a gate failure, fix it, enter beta, gather votes from test accounts and be promoted, all end to end.
- Verification spend per author is capped (configurable), so a malicious author can't run up the API bill.

## Out of scope
Discussion forums.
