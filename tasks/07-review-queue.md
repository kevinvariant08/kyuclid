# 07. Build the review queue

## Goal
Give Kevin a fast way to approve, edit or reject verified drafts. Approved problems become live in the bank, and rejection reasons flow back into the generator's prompts.

## Depends on
01 (schema and scripts) and 05 (verification reports).

## Read first
- `schema/problem.schema.json`, `pipeline/verify/` report format, `scripts/hash-answer.mjs`.

## Deliverables
1. `tools/review.html`: a local-only page served by `python -m http.server`, **not** linked from the site and not deployed (put it in a folder excluded from Pages, or gate it). It shows one draft at a time:
   - The statement rendered with MathJax, the figure, the answer, hints and solution.
   - A summary of the verification report: the blind-solve agreement, the estimated kyu, the originality nearest neighbour (as an ID only), cost.
   - Buttons for **Approve**, **Approve with edits**, **Reject** and **Skip**. Rejecting needs a reason: pick from the standard's failure list (task 04) and optionally add a note.
   - Inline editing of the statement, solution, hints, kyu and title, with a live preview.
   - Keyboard shortcuts (`a` approve, `r` reject, `e` edit, `j`/`k` next and previous) and a progress counter.
2. `scripts/review-server.mjs`: a tiny local server so the page can write files. Decisions are written to:
   - Approve → `data/problems/<id>.json` in final schema form: with `answer_hash` and with the plain `answer`, `check_program` and `inspired_by` stripped out. Set `status: "beta"`, then rebuild `data/index.json`.
   - Reject → `review/rejected/<id>.json` with the reason.
   - Every decision is appended to `review/decisions.jsonl` (ID, decision, reason, edits diff, time).
3. Edited problems are **re-verified** (task 05) before they are saved, since an edit can break the answer.
4. `scripts/rejection-digest.mjs` summarises the rejection reasons into a short paragraph that the generator's prompt can include (task 06 reads it).

## Acceptance criteria
- Reviewing 20 drafts takes Kevin under 15 minutes, excluding thinking time.
- An approved problem shows up on the site after `build-index` and a push, with the answer checked correctly.
- Editing an answer-bearing statement triggers re-verification, and a failing edit is blocked with the reason shown.
- `review/pending/` is in `.gitignore` if drafts might reveal `inspired_by`. Only final problem files are committed.

## Out of scope
Public community review (17).
