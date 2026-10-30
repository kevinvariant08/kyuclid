# 11. Replace the seed set and fill the ladder

## Goal
Retire the 21 draft problems where they don't meet the standard, and make sure every belt has enough reviewed problems for launch.

## Depends on
06, 07 and 08. It also uses 09 for 3–1 kyu.

## Spec
1. Run all 21 seed problems through the verification gate (05) and the standard (04). Then follow these rules:
   - Keep any that pass, with `provenance.kind` set correctly.
   - Retire the rest by setting `status: "retired"`, and add that value to the schema if task 01 didn't. Don't delete them, so that old links still resolve, but hide them from lists.
   - The two AIME problems reproduced in the draft (AIME 1985 P10, AIME 1990 P11) must be retired, or replaced by originals that use their ideas, unless Kevin decides otherwise.
2. **Launch minimums** for problems with `status` ranked or beta:

   | kyu | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 |
   |---|---|---|---|---|---|---|---|---|
   | problems | 60 | 60 | 60 | 100 | 100 | 100 | 20 | 10 |

   Each topic needs at least 15% of its kyu, except at 2–1 kyu.
3. Update the homepage copy and the "belt rack" counts so they come from `data/index.json` rather than being hard-coded.
4. Remove "first draft" wording from the site once the minimums are met.

## Acceptance criteria
- `scripts/validate.mjs` reports the counts table and passes the minimums.
- No retired problem appears in any list or in the problem of the day, but its URL still loads with a "retired" note.

## Out of scope
Generating new problems: if a cell is short, raise it in the PR so tasks 06, 08 or 09 can run again.
