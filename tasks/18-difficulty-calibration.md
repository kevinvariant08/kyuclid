# 18. Calibrate kyu from real solve data

## Goal
Once real players are solving, re-estimate each problem's difficulty from data, so that kyu labels match reality. A 4 kyu problem should be one a typical 4 kyu player solves about half the time.

## Depends on
13. It needs real attempts, so schedule it a few weeks after accounts launch.

## Read first
- Kevinvariant's `KEVINVARIANT_ADAPTIVE_BRIEF.md`, `calibration/` and `smart.js`. Kevinvariant already fits an item-response model (an ability scale θ, item ratings, a logistic success probability) for TMUA questions. Reuse the approach and the code where it fits.

## Spec
1. **The model.** Use a Rasch-style or two-parameter logistic item response model, or Elo with simultaneous player and problem ratings (as Codeforces does). Inputs are first attempts only, with hints counting as partial failure. Fit nightly in a scheduled job: a GitHub Action calling a Supabase function, or a Python job.
2. **Mapping to kyu.** Set kyu boundaries on the problem-rating scale so that the current labelled bank is preserved as closely as possible, then let individual problems move.
3. **Guard rails:**
   - A problem needs at least 40 attempts before its kyu can change.
   - It moves at most one kyu per month.
   - Proof problems are excluded.
   - Every change is logged, and Kevin gets a weekly digest.
4. **Dashboard.** An admin-only page shows problems whose data disagrees most with their label, the distribution of player ratings, and the solve rate by kyu.
5. **Feedback to generation.** Export systematic biases, such as "generated geometry at 4 kyu is consistently easier than labelled", to a report that task 06 prompts can use.

## Acceptance criteria
- On simulated data with known true difficulties (generate it), the fitted ranking correlates at 0.9 or better with the truth.
- Guard rails are enforced and tested.

## Out of scope
Changing the points formula.
