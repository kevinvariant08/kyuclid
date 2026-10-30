# 02. Build the private AIME corpus

## Goal
Collect every AIME problem from the last 15 years, with official answers and links to solutions, as clean machine-readable data. The data is for private analysis only and feeds tasks 03 and 06. It is never published.

## Depends on
Nothing.

## Read first
- `tasks/README.md`, especially rule 1, which says contest texts stay private.

## Scope
- **AIME I and AIME II, 2012–2026**: 15 years × 2 papers × 15 problems = **450 problems**. Years with only one paper or with an extra paper (such as 2021 AIME I and II, and any year with a reissued paper) are recorded as they actually happened. Note any deviation from 450 in the report.
- Design the format so that AMC 8, AMC 10/12, UKMT (JMC, IMC, SMC, JMO, Hamilton, Maclaurin), BMO1 and BMO2 can be added later with no schema change. Task 08 adds them.

## Where it lives
- Create a **private** GitHub repository, `kevinvariant08/mathwars-corpus`. Ask Kevin to create it if you can't. Never put corpus files in the public `mathwars` repo.
- Layout:
  ```
  raw/<exam>/<year>/<paper>.html         cached source pages, fetched once
  corpus/aime.jsonl                      one problem per line
  corpus/SOURCES.md                      where each file came from and when
  scripts/fetch_aime.py
  scripts/parse_aime.py
  scripts/check_corpus.py
  ```

## Record format (`corpus/aime.jsonl`)
```json
{"id":"AIME-2019-I-07","exam":"AIME","year":2019,"paper":"I","number":7,
 "statement_md":"... with $LaTeX$ ...","answer":"057","answer_int":57,
 "has_figure":true,"figure_source":"asy code or image URL, verbatim",
 "solution_urls":["https://artofproblemsolving.com/wiki/index.php/2019_AIME_I_Problems/Problem_7"],
 "source_url":"...","fetched_at":"2026-10-30T12:00:00Z"}
```

## Spec
1. **Source.** The Art of Problem Solving wiki has a page per problem plus an answer key per paper. Read its terms of use and `robots.txt` first, and stop and report if automated fetching isn't allowed. Fetch politely: at most 1 request every 2 seconds, with a descriptive User-Agent, caching everything in `raw/` so each page is fetched only once. If Kevin owns official MAA PDFs, they are a better source for statements, so ask.
2. **Parse** the statements into Markdown with `$…$` LaTeX. Convert `<img>` LaTeX renders back to their `alt` LaTeX. Keep Asymptote code verbatim in `figure_source`.
3. **Answers** come from the official answer key page, not from solution text. AIME answers are integers from 000 to 999.
4. `check_corpus.py` checks the following and prints a summary:
   - The count per year and paper, flagging anything other than 15.
   - Every answer is an integer from 0 to 999.
   - IDs are unique.
   - There are no empty statements and no leftover HTML tags.
   - LaTeX parses, checked by a MathJax or KaTeX dry run in Node.
   - It lists the problems that have figures.
5. **Spot-check.** Choose 20 problems at random and compare them by eye with the source. Record the result in `corpus/SOURCES.md`.

## Acceptance criteria
- `corpus/aime.jsonl` has every AIME problem from 2012–2026, and any gap is explained.
- `check_corpus.py` passes, and the 20-problem spot-check found no errors.
- Nothing from the corpus appears in the public `mathwars` repo. Run a check with `git grep` for a distinctive phrase from three problems.

## Out of scope
Analysing problems (task 03), generating problems (task 06), other exams (task 08).
