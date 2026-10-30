# 16. Proof submission and review

## Goal
Let players submit written proofs for 3–1 kyu problems and get a fair mark out of 7. The mark comes from an AI first pass plus review by higher-ranked players, with Kevin moderating.

## Depends on
09 (proof problems with rubrics) and 13 (accounts).

## Read first
- Kevinvariant's Proof marker (`marker.html`, `marker-admin.html`, `marker-problems.sql`). It already marks written solutions with a model through a server-side proxy (the Cloudflare Worker in `worker/`). Reuse its prompt design and proxy pattern, and don't call the model from the browser with a secret.

## Spec
1. **Submission.** The current LaTeX editor with live preview, plus an image upload for handwritten work (stored in Supabase Storage, 5 MB max). A proof is locked once submitted. One live submission per problem per user, with resubmission allowed after it is marked.
2. **AI first pass.** The server marks the proof against the rubric with `claude-opus-5-5`, giving each rubric line's marks with a quoted justification. It flags suspected copying, for example near-identical text to another submission or to the model solution. Show this to the solver as "provisional".
3. **Peer review:**
   - Each submission goes to two reviewers whose rank is at least 1 kyu above the problem and who have solved it.
   - Reviewers see the rubric, the AI marks and the proof, never the author's handle.
   - They confirm or adjust each rubric line and give a short comment.
   - The final mark is the median of the AI and the two reviewers.
   - If the reviewers differ by 3 marks or more, the submission goes to Kevin.
4. **Honour points.** Reviewers earn honour points, which are separate from rank points, for reviews that end up within one mark of the final.
5. **Points.** The solver gets `kyu points × final mark ÷ 7`. A final mark of 5 or more counts as "solved" and unlocks the official solution.
6. **Moderation.** An admin page lists disputes, flagged copying and reports.

## Acceptance criteria
- The full flow works end to end with test accounts, including a dispute that escalates.
- Reviewers can't see author identities, and authors can't see reviewer identities. Check this with direct API calls.
- The AI first pass never sees or reveals other users' submissions.

## Out of scope
Live mentoring and comment threads on problems.
